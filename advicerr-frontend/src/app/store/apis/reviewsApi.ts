import { createApi } from '@reduxjs/toolkit/query/react'
import { TAdminReview, TAdminReviewDeleteResponse, TReviewToCreate } from '@/app/types/ReviewTypes'
import { apiBaseQuery } from './apiClient'


export const reviewsApi = createApi({
  reducerPath: 'reviewsApi',
  baseQuery: apiBaseQuery,
  endpoints: (builder) => ({
    createReview: builder.mutation<void, TReviewToCreate>({
      query: (body) => ({
        url: `reviews/`,
        method: "POST",
        body: body
      })
    }),
    getAdminReviews: builder.query<Array<TAdminReview>, string>({
      query: (token) => ({
        url: `reviews/admin/all`,
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })
    }),
    deleteAdminReview: builder.mutation<TAdminReviewDeleteResponse, { token: string; reviewId: string }>({
      query: ({ token, reviewId }) => ({
        url: `reviews/${reviewId}`,
        method: "DELETE",
        headers: {
          "Authorization": `Bearer ${token}`
        }
      })
    })
  }),
})

export const { useCreateReviewMutation, useGetAdminReviewsQuery, useDeleteAdminReviewMutation } = reviewsApi
