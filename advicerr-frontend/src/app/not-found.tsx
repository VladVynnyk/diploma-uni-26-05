"use client"
import React from 'react'
import usePrefixedTranslation from './hooks/usePrefixedTranslation'

type Props = {}

const NotFoundPage = (props: Props) => {
  const { t } = usePrefixedTranslation('Pages.NotFoundPage');

  return (
    <div className="grid h-screen place-content-center bg-white px-4">
        <div className="text-center">
            <h1 className="text-9xl font-black text-gray-200">{t('headerTitle')}</h1>   {/*404*/}

            <p className="text-2xl font-bold tracking-tight text-gray-900 sm:text-4xl">{t('uhOhMessage')}</p>

            <p className="mt-4 text-gray-500">{t('message')}</p>

            <a
            href="/"
            className="mt-6 inline-block rounded bg-teal-500 px-5 py-3 text-sm font-medium text-white hover:bg-teal-700 focus:outline-none focus:ring"
            >
            {t('goBackButton')}
            </a>
        </div>
    </div>
  )
}

export default NotFoundPage