from erp_sync.Resources.resource import Resource

class BillPayments(Resource):

    urls = {}
    
    def set_company_id(self,company_id):
        super().set_company_id(company_id)
        self._set_urls()
        return self

    def _set_urls(self):

        self.urls = {
            "new": f"/companies/{super().get_company_id()}/payments",
            "edit": f"/companies/{super().get_company_id()}/payments",
            "delete": f"/companies/{super().get_company_id()}/payments",
            "import": f"/companies/{super().get_company_id()}/import_payments"
        }

        super().set_urls(self.urls)

        return self
        
    def edit(self,ledger_id = None, payload = None, method='PUT',endpoint=None):
        
        self._set_urls()

        self.urls["edit"] = f'{self.urls["edit"]}/{ledger_id}'

        super().set_urls(self.urls)
        
        return super().edit(payload, method, endpoint)

    def delete(self, ledger_id=None, payload=None, method='DELETE', endpoint=None):

        self._set_urls()

        payload = {"type": "PurchasePayment"}

        self.urls["delete"] = f'{self.urls["delete"]}/{ledger_id}'

        super().set_urls(self.urls)

        return super().delete(payload, method, endpoint)
        
    def import_data(self,ledger_id = None, payload = None, method='GET',endpoint=None):
        
        self._set_urls()

        if ledger_id is not None:
            self.urls["import"] = f'{self.urls["import"]}/{ledger_id}'
            super().set_urls(self.urls)
            
        return super().import_data(payload, method, endpoint)

    def payload(self):

        data = {
            "amount": "<Enter amount>",
            "vendor_id": "<Enter vendor id>",
            "reference": "<Enter unique reference>",
            "description": "<Enter description>",
            "date": "<Enter date (yyyy-mm-dd) e.g. 2021-11-22>"
        }

        return data

    def serialize(self, payload=None, operation=None):

        data = {}

        if operation is None:
            return "Specify the operation: Resource.READ, Resource.NEW or Resource.UPDATE"

        if operation == super().NEW or operation == super().UPDATE:

            data["type"] = "PurchasePayment"

            if 'type' in payload.keys():
                data["type"] = payload.get("type", "PurchasePayment")

            additional_properties = payload.get("additional_properties", {})

            # If client type is Quickbooks Online
            if super().get_client_type() == super().QBO: 
                
                self.urls.update({
                    "new": f"/companies/{super().get_company_id()}/vendor_payments",
                    "edit": f"/companies/{super().get_company_id()}/vendor_payments",
                })

                super().set_urls(self.urls)           

                data = {"type": "PurchasePayment"}

                if 'type' in additional_properties.keys():
                    data.update({
                        "type": additional_properties.get("type", "PurchasePayment")
                    })

                    additional_properties.pop("type")

                if 'amount' in payload.keys():
                    data.update({
                        "TotalAmt": payload.get("amount", 0)
                    })

                if 'pay_type' in payload.keys():
                    data.update({
                        "PayType": payload.get("pay_type", 0)
                    })

                if 'vendor_id' in payload.keys():
                    data.update({
                        "VendorRef": {
                            "value": payload.get("vendor_id", "")
                        }
                    })

                if 'currency_code' in payload.keys():
                    data.update({
                        "CurrencyRef": {
                            "value": payload.get("currency_code", "KES")
                        }
                    })

                invoices = payload.get("invoice_payments", [])

                for i in range(len(invoices)):
                    invoice = {}
                    if 'amount' in invoices[i].keys():
                        invoice.update({
                            "Amount": invoices[i].get("amount", "")
                        })

                    if 'invoice_id' in invoices[i].keys():
                        invoice.update({
                            "LinkedTxn": [
                                {
                                    "TxnId": invoices[i].get('invoice_id',""),
                                    "TxnType": payload.get("payment_type", "Bill")
                                }
                            ]
                        })
                    
                    invoices[i] = invoice

                # if invoices has data in it
                if bool(invoices):
                    data.update({
                        "Line": invoices
                    })

            # If client type is ZOHO
            elif super().get_client_type() == super().ZOHO:

                data = {"type": "PurchasePayment"}

                if 'type' in additional_properties.keys():
                    data.update({
                        "type": additional_properties.get("type", "PurchasePayment")
                    })

                    additional_properties.pop("type")

                if 'vendor_id' in payload.keys():
                    data.update({
                        "vendor_id": payload.get("vendor_id", "")
                    })

                if 'amount' in payload.keys():
                    data.update({
                        "amount": payload.get("amount", "")
                    })

                if 'date' in payload.keys():
                    data.update({
                        "date": payload.get("date", "")
                    })
                
                invoices = payload.get("invoice_payments", [])

                for i in range(len(invoices)): 
                    if i == 0:
                        if 'payment_reference' in invoices[i].keys():
                            data.update({
                                "reference_number": invoices[i].pop('payment_reference')
                            })
                        if 'account_id' in invoices[i].keys():
                            data.update({
                                "paid_through_account_id": invoices[i].pop('account_id')
                            })
                    
                    if 'invoice_id' in invoices[i].keys():
                        invoices[i]['bill_id'] = invoices[i].pop('invoice_id')
                    if 'amount' in invoices[i].keys():
                        invoices[i]['amount_applied'] = invoices[i].pop('amount')
                            
                    if 'payment_date' in invoices[i].keys():
                        invoices[i].pop('payment_date')                            
                    if 'payment_type' in invoices[i].keys():
                        invoices[i].pop('payment_type')

                # if invoices has data in it
                if bool(invoices):
                    data.update({
                        "bills": invoices
                    })

            # If client type is MS_DYNAMICS
            elif super().get_client_type() == super().MS_DYNAMICS:
                data.pop("type")
                data.update({
                    # "paymentReference": payload.get("reference", ""),
                    "ownerInvoiceType": "Vendor",
                    # "ownerInvoiceNumber": payload.get("invoice_id", ""),
                    "ownerNumber": payload.get("vendor_id", ""),
                    "description": payload.get("description", ""),
                    # "amount": payload.get("amount", 0),
                    "bankCode": payload.get("bank_code", ""),
                })
                invoice = payload.get("invoice_payments", [])

                if bool(invoice):
                    if "invoice_id" in invoice[0].keys():
                        data.update({
                            "ownerInvoiceNumber": invoice[0].pop("invoice_id"),
                        }) 
                    if 'payment_reference' in invoice[0].keys():
                        data.update({
                            "paymentReference": invoice[0].pop('payment_reference')
                        })
                    if 'amount' in invoice[0].keys():
                        data.update({
                            "amount": invoice[0].pop('amount')
                        })                    
                    
                    if 'payment_date' in invoice[0].keys():
                        invoice[0].pop('payment_date')
                    if 'payment_type' in invoice[0].keys():
                        invoice[0].pop('payment_type')
                    if 'account_id' in invoice[0].keys():
                        invoice[0].pop('account_id')

            data.update(additional_properties)

            return data

        elif operation == super().READ:

            payload = super().response()

            data = payload

            # confirms if a single object was read from the database
            if isinstance(payload, dict):
                if 'resource' in payload.keys():
                    data = payload.get("resource", [])
                
            # confirms if a single object was read from the database
            if isinstance(data, dict):
                data = [data]
            
            # confirms if data is a list
            if isinstance(data, list):
                if len(data) > 0:
                    for i in range(len(data)):
                        if 'chart_of_account_id' in data[i].keys():
                            data[i]['vendor_id'] = data[i].pop('chart_of_account_id')           
                        if 'reference_number' in data[i].keys():
                            data[i]['reference'] = data[i].pop('reference_number')          
                        if 'total_amount' in data[i].keys():
                            data[i]['amount'] = data[i].pop('total_amount')
                        
            if 'resource' in payload.keys():
                payload["resource"] = data

            super().set_response(payload)

            return self

