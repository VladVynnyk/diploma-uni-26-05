import React from 'react'
import Signup from './SignUpWContainer'
import { signUpMetadata } from './metadata'

type Props = {}

export const metadata = signUpMetadata

const SignUpPage = (props: Props) => {
  return (
    <Signup/>
  )
}

export default SignUpPage