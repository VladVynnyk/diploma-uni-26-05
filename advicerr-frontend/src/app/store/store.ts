import { configureStore } from '@reduxjs/toolkit'
import { setupListeners } from '@reduxjs/toolkit/query'
import { usersApi } from './apis/usersApi'
import { paymentsApi } from './apis/paymentsApi'
import { ordersApi } from './apis/ordersApi'
import { reviewsApi } from './apis/reviewsApi'
import { passwordRecoverApi } from './apis/passwordRecoverApi'
import { tagsApi } from './apis/tagsApi'

export const store = configureStore({
  reducer: {
    [usersApi.reducerPath]: usersApi.reducer,
    [paymentsApi.reducerPath]: paymentsApi.reducer,
    [ordersApi.reducerPath]: ordersApi.reducer,
    [reviewsApi.reducerPath]: reviewsApi.reducer,
    [passwordRecoverApi.reducerPath]: passwordRecoverApi.reducer,
    [tagsApi.reducerPath]: tagsApi.reducer
  },

  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(usersApi.middleware, paymentsApi.middleware, ordersApi.middleware, 
      reviewsApi.middleware, passwordRecoverApi.middleware, tagsApi.middleware),
})

// setupListeners(store.dispatch)
export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch