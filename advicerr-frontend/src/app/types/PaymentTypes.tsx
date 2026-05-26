

export type TPayment = {
    // Here's mock data
    id: number;
    name: string;
}


export type TCreatePaymentRequest = {
    request: {
        server_callback_url: string,
        order_id: string,
        merchant_id: number,
        order_desc: string,
        amount: number,
        currency: string,
        signature: string
    }
}