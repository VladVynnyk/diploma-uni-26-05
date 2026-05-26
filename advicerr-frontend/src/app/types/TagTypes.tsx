export type TTag = {
    created_at: string,
    description: string,
    id: string,
    name: string
}

export type TTagForUpdate = {
  description: string,
  name: string
}

export type TTagPayload = {
  name: string,
  description: string
}
