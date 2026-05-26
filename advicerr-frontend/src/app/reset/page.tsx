import React from 'react'
import ResetPassword from './ResetPassword'

import { resetMetadata } from './metadata'

type Props = {}

export const metadata = resetMetadata

const ResetPasswordPage = (props: Props) => {
  return (
    <div><ResetPassword/></div>
  )
}

export default ResetPasswordPage