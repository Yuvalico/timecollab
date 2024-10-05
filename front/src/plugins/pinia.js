import { createPinia } from 'pinia'
import persistedstate from 'pinia-plugin-persistedstate' // Import the plugin

export const store = createPinia()

store.use(persistedstate)

export default function (app) {
  app.use(store)
}
