import { createApi } from '@reduxjs/toolkit/query/react'
import { TAdminStats, TCompleteRegistrationPayload, TMeUser, User,TUserTokens, TUserToRegister, TUserToUpdate, PaginatedUserResponse } from "../../types/UserTypes"
import { apiBaseQuery } from "./apiClient";


export const usersApi = createApi({
  reducerPath: 'usersApi',
  baseQuery: apiBaseQuery,
  endpoints: (builder) => ({
    getAllUsers: builder.query<Array<User>, void>({
      query: () => `users/`,
      // keepUnusedDataFor: 0,
    }),
    getPaginatedUsers: builder.query<PaginatedUserResponse, {page: number, pageSize: number}>({
      query: ({page, pageSize}) => ({
        url: `users/paginated`,
        params: {page, page_size: pageSize},
        keepUnsusedDataFor: 0
      })
    }),
    getPaginatedUsersWTags: builder.query<PaginatedUserResponse, {tagName: string, page: number, pageSize: number}>({
      query: ({tagName, page, pageSize}) => ({
        url: `users/sort_by_tag/${tagName}`,
        params: {page, page_size: pageSize},
        keepUnsusedDataFor: 0
      })
    }),
    getUsersWOffset: builder.query<Array<User>, {offset: number, limit: number}>({
      query: ({offset, limit}) => ({
        url: `users/offset`,
        params: {offset, limit},
        keepUnsusedDataFor: 0
      })
    }),
    getMe: builder.query<TMeUser, string>({
       query: (token) => ({
         url: `users/account/me`,
         headers: {
          "Authorization": `Bearer ${token}`
         }
       })
    }),
    getAdminUsers: builder.query<Array<User>, string>({
      query: (token) => ({
        url: `users/admin/all`,
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })
    }),
    updateAdminStatus: builder.mutation<User, { token: string; userId: string; is_admin: boolean }>({
      query: ({ token, userId, is_admin }) => ({
        url: `users/${userId}/admin-status`,
        method: 'PATCH',
        headers: {
          "Authorization": `Bearer ${token}`
        },
        body: { is_admin }
      })
    }),
    getAdminStats: builder.query<TAdminStats, string>({
      query: (token) => ({
        url: `dashboard/admin/stats`,
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })
    }),
    loginUser: builder.mutation<TUserTokens, FormData>({
      query: (formData) => ({
        url: 'auth/login',
        method: 'POST',
        body: formData
      })
    }),
    registerUser: builder.mutation<User, TUserToRegister>({
      query: (body) => ({
        url: 'auth/signup',
        method: 'POST',
        body: body
      })
    }),
    completeRegistration: builder.mutation<TUserTokens, TCompleteRegistrationPayload>({
      query: (body) => ({
        url: 'auth/complete-registration',
        method: 'POST',
        body
      })
    }),
    updatePhoto: builder.mutation<any, {id: string, formData: object}>({
      query: ({id, formData}) => ({
        url: `users/change/photo?user_id=${id}`,
        method: 'PATCH',
        body: formData
      })
    }),
    updateUser: builder.mutation<User, { id: string; body: TUserToUpdate }>({
      query: ({ id, body }) => ({
        url: `users/update/${id}`,
        method: 'PATCH',
        body: body
      })
    }),
    refreshToken: builder.mutation<any, any>({
      query: (body) => ({
        url: `auth/refresh-token`,
        method: 'POST',
        // body: {"refresh_token": refreshToken}
        body: body
      }),
    })
  }),
})

export const { useGetAllUsersQuery, useGetPaginatedUsersQuery, 
              useGetPaginatedUsersWTagsQuery, useGetUsersWOffsetQuery, 
              useGetMeQuery, useGetAdminUsersQuery, useGetAdminStatsQuery, useLoginUserMutation, 
              useRegisterUserMutation, useCompleteRegistrationMutation, useUpdatePhotoMutation, useUpdateUserMutation, 
              useRefreshTokenMutation, useUpdateAdminStatusMutation } = usersApi
