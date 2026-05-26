import { TTag } from "./TagTypes"

export type TUser = {
    id: string,
    first_name: string,
    last_name: string,
    email?: string,
    phone_number?: string,
    tags: Array<TTag>
}


export type Order = {
    client_id: string,
    consultant_id: string,
    created_at: string,
    duration_minutes: number,
    id: string,
    message: string,
    price: number,
    scheduled_at: string | null,
    status: "new" | "confirmed" | "in_progress" | "completed" | "cancelled",
    topic: string,
    client: TUser,
    consultant: TUser
}

export type TConsultationRequestBase = {
    consultant_id: string,
    price: number,
    topic: string,
    message: string,
    scheduled_at: string | null,
    duration_minutes: number,
}

export type TOrderForRegisteredUser = {
    consultation: TConsultationRequestBase & {
        client_id: string,
    }
}

export type TOrderForUnregisteredUser = {
    consultation: TConsultationRequestBase & {
        first_name: string,
        last_name: string,
        phone_number: string,
        email: string
    }
}

export type TOrderStatusUpdate = {
    status: Order["status"]
}

export type TOrderAuthFlow = {
    email: string | null,
    requires_complete_registration: boolean,
    should_login: boolean,
    message: string | null
}

export type TCreateOrderResponse = {
    order: Order,
    auth_flow: TOrderAuthFlow
}

export const ORDER_STATUS_TRANSITIONS: Record<Order["status"], Array<Order["status"]>> = {
    new: ["confirmed", "cancelled"],
    confirmed: ["in_progress", "cancelled"],
    in_progress: ["completed", "cancelled"],
    completed: [],
    cancelled: [],
}
