from datetime import datetime
from typing import Any, Dict, Optional

import boto3
from fastapi import Response
from fastapi.responses import HTMLResponse, RedirectResponse

from fastel.cart import Cart
from fastel.cart.datastructures import InvoiceTypes, PaymentSubTypes
from fastel.collections import get_collection
from fastel.config import SdkConfig
from fastel.payment.common.models.callback import CallbackModel
from fastel.payment.common.models.order import Order
from fastel.payment.neweb.gateway import NewebInvoice, Newebpay
from fastel.payment.neweb.models.callback import (
    CallbackMsg,
    EncryptedCallback,
    GetNumMsg,
)
from fastel.payment.neweb.models.checkout import CheckoutModel
from fastel.payment.neweb.models.invoice import IssueModel, IssueResp
from fastel.payment.utils import PaymentStatus


class NewebpayCheckout:
    def __init__(self, notify_url: str, customer_url: str, return_url: str) -> None:
        self.gateway = Newebpay(
            SdkConfig.neweb_merchant_id,
            SdkConfig.neweb_hash_key,
            SdkConfig.neweb_hash_iv,
            stage=SdkConfig.stage,
        )
        self.notify_url = notify_url
        self.customer_url = customer_url
        self.return_url = return_url

    def __call__(self, cart: Cart, **kwargs: Any) -> HTMLResponse:
        checkout_model = self.parse_payload(cart, **kwargs)
        cart_dict = cart.get_cart_ins()
        del cart_dict["_id"]
        checkout_ins = {
            **cart_dict,
            "payment_transaction_detail": checkout_model.dict(),
            "payment_transaction_id": checkout_model.MerchantOrderNo,
        }
        get_collection("checkout").insert_one(checkout_ins)
        return HTMLResponse(self.gateway.checkout_request(checkout_model))

    def parse_payload(self, cart: Cart, **kwargs: Any) -> CheckoutModel:
        timestamp = str(int(datetime.now().timestamp() * 1000))
        type_map = {}
        if cart.payment_subtype == PaymentSubTypes.credit:
            type_map["CREDIT"] = 1
        elif cart.payment_subtype == PaymentSubTypes.atm:
            type_map["VACC"] = 1
        elif cart.payment_subtype == PaymentSubTypes.linepay:
            type_map["LINEPAY"] = 1
        elif cart.payment_subtype == PaymentSubTypes.cod:
            type_map["CVSCOM"] = 1

        return CheckoutModel(
            Amt=cart.total,
            ItemDesc=cart.items.items[0].name,
            MerchantOrderNo=timestamp,
            Email=cart.buyer_email,
            NotifyURL=self.notify_url,
            CustomerURL=self.customer_url,
            ReturnURL=self.return_url,
            **type_map,
            **kwargs,
        )


class NewebpayCallback:
    def __init__(self) -> None:
        self.gateway = Newebpay(
            SdkConfig.neweb_merchant_id,
            SdkConfig.neweb_hash_key,
            SdkConfig.neweb_hash_iv,
            stage=SdkConfig.stage,
        )

    def __call__(self, data: Dict[str, Any]) -> CallbackModel:
        validated = self.validate(data)
        decrypted = self.gateway.decrypt_callback(validated)
        parsed = self.parse_payload(decrypted)
        return parsed

    def validate(self, data: Dict[str, Any]) -> EncryptedCallback:
        return EncryptedCallback.validate(data)

    def parse_payload(self, decrypted: CallbackMsg) -> CallbackModel:
        if decrypted.Status == "SUCCESS":
            payment_status = PaymentStatus.SUCCESS
        else:
            payment_status = PaymentStatus.FAILURE

        result = decrypted.Result
        if result.PaymentType == "CREDIT":
            payment_subtype = PaymentSubTypes.credit
        elif result.PaymentType == "VACC":
            payment_subtype = PaymentSubTypes.atm
        elif result.PaymentType == "CVSCOM":
            payment_subtype = PaymentSubTypes.cod
        elif result.PaymentType == "BARCODE":
            payment_subtype = PaymentSubTypes.barcode
        elif result.PaymentType == "WEBATM":
            payment_subtype = PaymentSubTypes.webatm
        else:
            payment_subtype = PaymentSubTypes.unknown

        return CallbackModel(
            payment_status=payment_status,
            order_id=decrypted.Result.MerchantOrderNo,
            payment_subtype=payment_subtype,
            payment_transaction_detail=result.dict(),
            total=result.Amt,
        )

    def respond(self) -> Response:
        return Response(content="1")


class NewebpayGetNumber:
    def __init__(self) -> None:
        self.gateway = Newebpay(
            SdkConfig.neweb_merchant_id,
            SdkConfig.neweb_hash_key,
            SdkConfig.neweb_hash_iv,
            stage=SdkConfig.stage,
        )

    def __call__(self, data: Dict[str, Any]) -> CallbackModel:
        validated = self.validate(data)
        decrypted = self.gateway.decrypt_getnum(validated)
        parsed = self.parse_payload(decrypted)
        return parsed

    def validate(self, data: Dict[str, Any]) -> EncryptedCallback:
        return EncryptedCallback.validate(data)

    def parse_payload(self, decrypted: GetNumMsg) -> CallbackModel:
        result = decrypted.Result
        if decrypted.Status == "SUCCESS":
            payment_status = PaymentStatus.CODE_GENERATED
        else:
            payment_status = PaymentStatus.FAILURE

        expire_date = result.ExpireDate
        expire_time = result.ExpireTime

        if result.PaymentType == "VACC":
            payment_subtype = PaymentSubTypes.atm
        elif result.PaymentType == "BARCODE":
            payment_subtype = PaymentSubTypes.barcode
        elif result.PaymentType == "CVS":
            payment_subtype = PaymentSubTypes.cvs

        bank_code: Optional[str] = ""
        bank_account: Optional[str] = ""

        code_no: Optional[str] = ""

        barcode_1: Optional[str] = ""
        barcode_2: Optional[str] = ""
        barcode_3: Optional[str] = ""

        if payment_subtype == PaymentSubTypes.atm:
            bank_code = result.BankCode
            bank_account = result.CodeNo
        elif payment_subtype == PaymentSubTypes.cvs:
            code_no = result.CodeNo
        elif payment_subtype == PaymentSubTypes.barcode:
            barcode_1 = result.Barcode_1
            barcode_2 = result.Barcode_2
            barcode_3 = result.Barcode_3

        return CallbackModel(
            payment_status=payment_status,
            order_id=result.MerchantOrderNo,
            payment_redirect_detail=result.dict(exclude_none=True),
            total=result.Amt,
            pay_deadline=f"{expire_date} {expire_time}",
            payment_subtype=payment_subtype,
            bank_code=bank_code,
            bank_account=bank_account,
            code_no=code_no,
            barcode_1=barcode_1,
            barcode_2=barcode_2,
            barcode_3=barcode_3,
        )

    def respond(self) -> Response:
        return Response(content="1")


class NewebInvoiceIssue:
    def __init__(self) -> None:
        self.gateway = NewebInvoice(
            merchant_id=SdkConfig.neweb_invoice_merchant_id,
            hash_key=SdkConfig.neweb_invoice_hash_key,
            hash_iv=SdkConfig.neweb_invoice_hash_iv,
            stage=SdkConfig.stage,
        )

    def __call__(self, order: Dict[str, Any]) -> IssueResp:
        validated = self.validate(order)
        parsed = self.parse_order(validated)
        return self.gateway.issue(parsed)

    def validate(self, order: Dict[str, Any]) -> Order:
        return Order.validate(order)

    def parse_order(self, order: Order) -> IssueModel:
        item_name = "|".join(list(map(lambda item: item.name, order.items)))
        item_count = "|".join(list(map(lambda item: str(item.config.qty), order.items)))
        item_unit = "|".join(list(map(lambda item: "個", order.items)))
        if order.invoice_type == InvoiceTypes.B2B:
            item_amount = "|".join(
                list(map(lambda item: str(round(item.sales_amount)), order.items))
            )
            item_price = "|".join(
                list(map(lambda item: str(item.unit_sales), order.items))
            )
        else:
            item_amount = "|".join(
                list(map(lambda item: str(item.amount), order.items))
            )
            item_price = "|".join(list(map(lambda item: str(item.price), order.items)))

        payload: Dict[str, Any] = {"BuyerName": order.buyer_name}

        if order.invoice_type == InvoiceTypes.B2B:
            payload["Category"] = "B2B"
            payload["BuyerUBN"] = order.b2b_company_no
            payload["BuyerName"] = order.b2b_company_name
            payload["PrintFlag"] = "Y"

        elif order.invoice_type == InvoiceTypes.B2C_DONATE:
            payload["Category"] = "B2C"
            payload["LoveCode"] = order.b2c_donate_code
            payload["PrintFlag"] = "N"

        elif order.invoice_type == InvoiceTypes.B2C_PHONE_CARRIER:
            payload["Category"] = "B2C"
            payload["CarrierType"] = "0"
            payload["CarrierNum"] = order.b2c_phone_carrier_code
            payload["PrintFlag"] = "N"

        elif order.invoice_type == InvoiceTypes.B2C_NPC:
            payload["Category"] = "B2C"
            payload["CarrierType"] = "1"
            payload["CarrierNum"] = order.b2c_npc_code
            payload["PrintFlag"] = "N"

        elif order.invoice_type == InvoiceTypes.B2C_PROVIDER:
            payload["Category"] = "B2C"
            payload["CarrierType"] = "2"
            payload["CarrierNum"] = order.buyer_email
            payload["PrintFlag"] = "N"

        elif order.invoice_type == InvoiceTypes.B2C:
            payload["Category"] = "B2C"
            payload["PrintFlag"] = "Y"

        invoice_id = str(int(datetime.now().timestamp() * 1000))
        return IssueModel(
            Status="1",
            MerchantOrderNo=invoice_id,
            Amt=order.sales,
            TaxAmt=order.tax,
            TotalAmt=order.total,
            TaxRate="5",
            TaxType="1",
            ItemName=item_name,
            ItemCount=item_count,
            ItemUnit=item_unit,
            ItemPrice=item_price,
            ItemAmt=item_amount,
            BuyerEmail=order.buyer_email,
            **payload,
        )


def get_checkout_method(prefix_path: str = "payment") -> NewebpayCheckout:
    if SdkConfig.default_payment_provider == "neweb":
        return NewebpayCheckout(
            notify_url=f"{SdkConfig.api_host}/{prefix_path}/callback",
            customer_url=f"{SdkConfig.api_host}/{prefix_path}/number",
            return_url=f"{SdkConfig.api_host}/{prefix_path}/return",
        )

    raise ValueError("unrecognize payment provider")


def get_callback_method() -> NewebpayCallback:
    if SdkConfig.default_payment_provider == "neweb":
        return NewebpayCallback()
    raise ValueError("unrecognize payment provider")


def get_getnum_method() -> NewebpayGetNumber:
    if SdkConfig.default_payment_provider == "neweb":
        return NewebpayGetNumber()
    raise ValueError("unrecognize payment provider")


def get_invoice_issue_method() -> NewebInvoiceIssue:
    if SdkConfig.default_payment_provider == "neweb":
        return NewebInvoiceIssue()
    raise ValueError("unrecognize payment provider")


stepfn = boto3.client("stepfunctions", "ap-northeast-1")


def process_callback(data: Dict[str, Any]) -> Response:
    callback_method = get_callback_method()
    callback_result = callback_method(data)
    stepfn.start_execution(
        stateMachineArn=SdkConfig.payment_stepfn_arn,
        name=f"callback_{callback_result.order_id}",
        input=callback_result.dict(),
    )

    return callback_method.respond()


def process_redirect(data: Dict[str, Any]) -> Response:
    callback_method = get_callback_method()
    callback_result = callback_method(data)
    return RedirectResponse(
        url=f"{SdkConfig.web_host}/profile/orders?action=detail&is_created=true&payment_transaction_id={callback_result.order_id}",
        status_code=302,
    )


def process_getnum(data: Dict[str, Any]) -> Response:
    getnum_method = get_getnum_method()
    getnum_result = getnum_method(data)
    stepfn.start_execution(
        stateMachineArn=SdkConfig.payment_stepfn_arn,
        name=f"getnum_{getnum_result.order_id}",
        input=getnum_result.dict(),
    )

    return getnum_method.respond()


def process_invoice_issue(order: Dict[str, Any]) -> IssueResp:
    issue_method = get_invoice_issue_method()
    issue_resp = issue_method(order)

    return issue_resp
