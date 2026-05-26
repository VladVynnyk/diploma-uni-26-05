import { createApi } from '@reduxjs/toolkit/query/react'
import { EmailRequest, RecoveryPasswordCodeRequest, RecoveryPasswordPasswordRequest } from '@/app/types/RequestsTypes';
import { apiBaseQuery } from './apiClient';


export const passwordRecoverApi = createApi({
  reducerPath: 'passwordRecoverApi',
  baseQuery: apiBaseQuery,
  endpoints: (builder) => ({
    sendCodeToEmail: builder.mutation<object, EmailRequest>({
      query: (body) => ({
        url: 'auth/recovery/send-code',
        method: 'PATCH',
        body: body
      })
    }),
    sendCodeToCheck: builder.mutation<object, RecoveryPasswordCodeRequest>({
      query: (body) => ({
        url: 'auth/recovery/check-code',
        method: 'PATCH',
        body: body
      })
    }),
    sendNewPassword: builder.mutation<object, RecoveryPasswordPasswordRequest>({
      query: (body) => ({
        url: `auth/recovery/password`,
        method: 'PATCH',
        body: body
      })
    }),
  }),
})

export const { useSendCodeToEmailMutation, useSendCodeToCheckMutation, useSendNewPasswordMutation } = passwordRecoverApi
