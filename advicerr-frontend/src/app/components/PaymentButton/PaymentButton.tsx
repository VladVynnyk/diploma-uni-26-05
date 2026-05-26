import React from 'react'
import { useRouter } from 'next/navigation'
import crypto from "crypto";

import { Button } from '@chakra-ui/react'

import { useCreatePaymentMutation } from '@/app/store/apis/paymentsApi';

import usePrefixedTranslation from '@/app/hooks/usePrefixedTranslation';
import { TCreatePaymentRequest } from "../../types/PaymentTypes"

type Props = {
    orderId: string,
    totalPrice: number
}


const PaymentButton = ({orderId, totalPrice}: Props) => {
    const { t } = usePrefixedTranslation("Components.PayButton")
    //@ts-ignore
    const dateOfOrder = Date.now()
    // console.log("dateOfOrder", dateOfOrder)
    // const description = '';
    const description = 'Оплата за консультацію';
    const router = useRouter()
    const [createPayment, { data, isSuccess, isLoading }] = useCreatePaymentMutation();
    
    const fondyPassword = 'test'
    
    const createSignature = (orderBody: object, fondyPassword: string) => {
        const orderedKeys = Object.keys(orderBody).sort((a, b) => {
            if (a < b) return -1;
            if (a > b) return 1;
            return 0;
        })
        
        //@ts-ignore
        const signatureRow = orderedKeys.map((v) => orderBody[v]).join('|')
        return crypto.createHash('sha1').update(`${fondyPassword}|${signatureRow}`).digest('hex')
    }

    // const router = useRouter()
    // const [createPayment, { data, isSuccess, isLoading }] = useCreatePaymentMutation();
    const handleClick = async () => {
    console.log("ROUTER: ", router)
        
        const orderBody = {
            server_callback_url: "https://advicerr.com/api/payments/proxy/accept-card-payment",
            order_id: `${orderId}`,
            merchant_id: 1396424,
            order_desc: description,
            amount: totalPrice*100,
            currency: "UAH"
        }
        
        const signature = createSignature(orderBody, fondyPassword)
    
        const request = {
            request: {
                server_callback_url: "https://advicerr.com/api/payments/proxy/accept-card-payment",
                order_id: `${orderId}`,
                merchant_id: 1396424,
                order_desc: description,
                amount: totalPrice*100,
                currency: "UAH",
                signature: signature
            }
        }
        
        try {
            console.log("HERE: ", request)
            const response = await createPayment(request).unwrap();
            // console.log("Url:", urlToPage)
            console.log("RESPONSE: ", response)
            router.push(response.response.checkout_url)
        } catch (error) {
            console.log(error)

            //console.log(error.config.data)
        }
    }

    return (
        <Button onClick={handleClick}>{t("payLabel")}</Button>
    )
}

export default PaymentButton
