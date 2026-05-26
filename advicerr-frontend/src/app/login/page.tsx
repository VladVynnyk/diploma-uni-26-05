import React, { Suspense } from 'react'
import LoginWContainer from './LoginWContainer'

import { loginMetadata } from './metadata'

type Props = {}

export const metadata = loginMetadata

const LoginPage = (props: Props) => {
  return (
    <Suspense fallback={null}>
      <LoginWContainer />
    </Suspense>
  )
}

export default LoginPage
