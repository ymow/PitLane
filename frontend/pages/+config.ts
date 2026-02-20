import vikeReact from 'vike-react/config'
import type { Config } from 'vike/types'
import Layout from '../layouts/Layout'

// Default config (can be overridden by pages)
export default {
  // https://vike.dev/Layout
  Layout,

  // https://vike.dev/Head
  title: 'PitLane F1 News',
  description: 'Global F1 News Platform',

  extends: vikeReact,
} satisfies Config
