import { createApi } from '@reduxjs/toolkit/query/react'
import { Order, TCreateOrderResponse, TOrderForRegisteredUser, TOrderForUnregisteredUser, TOrderStatusUpdate } from '@/app/types/OrderTypes'
import { apiBaseQuery } from './apiClient'


export const ordersApi = createApi({
  reducerPath: 'ordersApi',
  baseQuery: apiBaseQuery,
  endpoints: (builder) => ({
    getAllOrders: builder.query<Array<Order>, { id: string; token: string }>({
      query: ({ id, token }) => ({
        url: `orders/account/${id}`,
        headers: {
          "Authorization": `Bearer ${token}`
        }
      }),
    }),
    getAdminOrders: builder.query<Array<Order>, string>({
      query: (token) => ({
        url: `orders/admin/all`,
        headers: {
          "Authorization": `Bearer ${token}`
        }
      }),
    }),
    createOrder: builder.mutation<TCreateOrderResponse, TOrderForRegisteredUser | TOrderForUnregisteredUser>({
      query: (body) => ({
        url: "orders/",
        method: "POST",
        body: body
      }),
    }),
    updateOrderStatus: builder.mutation<Order, { token: string; orderId: string; body: TOrderStatusUpdate }>({
      query: ({ token, orderId, body }) => ({
        url: `orders/${orderId}/status`,
        method: "PATCH",
        headers: {
          "Authorization": `Bearer ${token}`
        },
        body
      }),
    }),
  }),
})

export const { useGetAllOrdersQuery, useGetAdminOrdersQuery, useCreateOrderMutation, useUpdateOrderStatusMutation } = ordersApi
