import { createApi } from '@reduxjs/toolkit/query/react'
import { TCreatePaymentRequest } from "../../types/PaymentTypes"
import { apiBaseQuery } from './apiClient'

export const paymentsApi = createApi({
  reducerPath: 'paymentsApi',
  baseQuery: apiBaseQuery,
  endpoints: (builder) => ({
    createPayment: builder.mutation<any, TCreatePaymentRequest>({
      query: (paymentBody) => ({
        url: '/payments/proxy/create-card-payment',
        method: 'POST',
        body: paymentBody
      })
    }),
    // acceptPayment: builder.mutation<any, TUserToRegister>({
    //   query: (body) => ({
    //     url: '/proxy/accept-card-payment',
    //     method: 'POST',
    //     body: body
    //   })
    // })
  }),
})

export const { useCreatePaymentMutation } = paymentsApi
