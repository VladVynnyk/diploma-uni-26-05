import React from 'react'
import LoginWContainer from './LoginWContainer'

import { loginMetadata } from './metadata'

type Props = {}

export const metadata = loginMetadata

const LoginPage = (props: Props) => {
  return (
    <LoginWContainer/>
)
}

export default LoginPage