import { createApi } from '@reduxjs/toolkit/query/react'
import { TTag, TTagPayload } from '@/app/types/TagTypes'
import { apiBaseQuery } from './apiClient'


export const tagsApi = createApi({
  reducerPath: 'tagsApi',
  baseQuery: apiBaseQuery,
  endpoints: (builder) => ({
    getTags: builder.query<Array<TTag>, void>({
      query: () => `tags/`,
    }),
    createTag: builder.mutation<TTag, { token: string; body: TTagPayload }>({
      query: ({ token, body }) => ({
        url: `tags/`,
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        },
        body
      })
    }),
    updateTag: builder.mutation<unknown, { token: string; id: string; body: TTagPayload }>({
      query: ({ token, id, body }) => ({
        url: `tags/${id}`,
        method: "PATCH",
        headers: {
          "Authorization": `Bearer ${token}`
        },
        body
      })
    }),
    deleteTag: builder.mutation<unknown, { token: string; id: string }>({
      query: ({ token, id }) => ({
        url: `tags/${id}`,
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })
    }),
  }),
})

export const { useGetTagsQuery, useCreateTagMutation, useUpdateTagMutation, useDeleteTagMutation } = tagsApi
