import { TTag } from "./TagTypes"

export type TReview = {
  client_id: string,
  consultant_id: string,
  created_at: string,
  description: string,
  id: string,
  rating: number
}

export type TReviewWClient = {
  client_id: string,
  consultant_id: string,
  created_at: string,
  description: string,
  id: string,
  rating: number
  client: {
    id: string,
    first_name: string,
    last_name: string,
    tags: Array<TTag>
  }
}

export type TAdminReview = TReview & {
  client: {
    id: string,
    first_name: string,
    last_name: string,
  } | null
}

export type TAdminReviewDeleteResponse = {
  id: string,
  client_id: string,
  consultant_id: string,
  description: string,
}

export type TReviewToCreate = {
  description: string,
  consultant_id: string,
  client_id: string,
  rating: number
}
