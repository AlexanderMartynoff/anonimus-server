const { configure } = require('quasar/wrappers')


module.exports = configure(function (ctx) {
  return {
    framework: {
      config: {
        // dark: true,
        screen: {
          bodyClasses: true,
        },
      },
      plugins: [
        'LocalStorage',
        'Cookies',
        'Dialog',
        'Notify',
      ]
    },
    supportTS: false,
    boot: [
      'service',
    ],
    extras: [
      'roboto-font',
      'material-icons',
    ],
    build: {
      vueRouterMode: 'history',

      chainWebpack(config) {
        config.plugin('define')
          .tap(definitions => {
            let [definition, ..._] = definitions

            definition.__VUE_OPTIONS_API__ = 'false'
            definition.__VUE_PROD_DEVTOOLS__ = 'false'
            definition.__VUE_PROD_HYDRATION_MISMATCH_DETAILS__ = 'false'

          return definitions
        })
      }
    },

    devServer: {
      proxy: {
        '/api': {
           target: 'ws://localhost:9000',
           ws: true,
           changeOrigin: true,
        },
      },
      server: {
        type: 'http'
      },
      port: 8080,
      open: false,
    },
  }
})
