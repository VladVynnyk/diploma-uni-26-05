import { TReview, TReviewWClient } from "./ReviewTypes"
import { TTag, TTagForUpdate } from "./TagTypes"

export type User = {
    id: string,
    last_name: string,
    phone_number?: string,
    email: string,
    description: string,
    created_at: string,
    first_name: string,
    photo: string,
    // price: number | string,
    price: number,
    rating: number,
    password: string,
    is_consultant: boolean,
    is_admin: boolean,
    reviews_as_consultant: Array<TReviewWClient>,
    tags: Array<TTag>
}

export type PaginatedUserResponse = {
    users: Array<User>,
    total_count: number,
    page: number,
    page_size: number
}


export type TMeUser = {
  email: string,
  description: string,
  created_at: string,
  first_name: string,
  id: string,
  is_admin: boolean,
  is_consultant: boolean,
  last_name: string,
  phone_number?: string,
  photo: string,
  price: number,
  password: string,
  reviews_as_consultant: Array<TReview>,
  tags: Array<TTagForUpdate>
}


export type TUser = {
    id: string,
    name: string,
    surname: string,
    photo: string,
    averageScore: number,
    pricePerHour: number,
    description: string,
    tags: Array<TTag>,
    reviews: Array<TReviewWClient>
}

export type TUserTokens = {
    access_token: string,
    refresh_token: string
}

export type TCompleteRegistrationPayload = {
    email: string,
    password: string,
    confirm_password: string
}

export type TUserToRegister = {
    first_name: string,
    last_name: string,
    email: string,
    password: string
}

export type TLoggedInUser = {
    email: string,
    description: string,
    created_at: string,
    first_name: string,
    id: string,
    is_admin: boolean,
    is_consultant: boolean,
    last_name: string,
    phone_number: string,
    photo: string,
    price: number,
    reviews_as_consultant: Array<TReview>,
    tags: Array<TTag>
}

export type TUserToUpdate = {
    last_name: string,
    phone_number?: string,
    email: string,
    description: string,
    first_name: string,
    photo: string,
    price: string,
    is_consultant: boolean,
    is_admin?: boolean,
    tags: Array<TTagForUpdate>
}

export type TAdminStats = {
  total_users: number,
  total_consultants: number,
  total_clients: number,
  total_orders: number,
  new_orders: number,
  confirmed_orders: number,
  in_progress_orders: number,
  completed_orders: number,
  cancelled_orders: number,
  total_reviews: number,
  average_rating: number,
  total_tags: number
}

