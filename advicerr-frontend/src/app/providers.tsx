'use client'
import { store } from "./store/store";
import { Provider } from "react-redux";

import { I18nextProvider } from "react-i18next";
import i18n from "./i18n"; // Import your i18n configuration

import { ChakraProvider } from '@chakra-ui/react'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <Provider store={store}>
      <ChakraProvider>
        <I18nextProvider i18n={i18n}>
          {children}
        </I18nextProvider>
      </ChakraProvider>
    </Provider>
  )
}