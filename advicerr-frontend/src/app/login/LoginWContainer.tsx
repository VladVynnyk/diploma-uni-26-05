"use client"
import React from 'react'
import MainContainer from "../components/MainContainer/MainContainer";
import LoginForm from '../components/LoginForm/LoginForm';


type Props = {}

const LoginWContainer = (props: Props) => {
  return (
    <MainContainer>
        <LoginForm/>
    </MainContainer>
  )
}

export default LoginWContainer