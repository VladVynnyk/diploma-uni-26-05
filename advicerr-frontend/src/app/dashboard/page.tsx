import React from 'react'

import Dashboard from './Dashboard'

import { dashboardMetadata } from './metadata'

type Props = {}

export const metadata = dashboardMetadata

const DashboardPage = (props: Props) => {
  return (
    <Dashboard/>
  )
}

export default DashboardPage