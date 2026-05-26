

export type EmailRequest = {
    email: string
}

export type RecoveryPasswordCodeRequest = {
    email: string
    code: string
}

export type RecoveryPasswordPasswordRequest = {
    email: string
    password: string
}