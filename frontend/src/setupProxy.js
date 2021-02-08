/* global require module process */

// import createProxyMiddleware from 'http-proxy-middleware';
const { createProxyMiddleware } = require('http-proxy-middleware');

const host = process.env.PROJECTX_HOST || '127.0.0.1:8000';

module.exports = (app) => {
  app.use(
    createProxyMiddleware(
      '/app/',
      {
        target: `http://${host}`,
        changeOrigin: true,
        xfwd: false,
      },
    ),
  );
  app.use(
    createProxyMiddleware(
      '/api/',
      {
        target: `http://${host}`,
        changeOrigin: true,
        xfwd: false,
      },
    ),
  );
  app.use(
    createProxyMiddleware(
      '/admin/',
      {
        target: `http://${host}`,
        changeOrigin: true,
        xfwd: false,
      },
    ),
  );
  app.use(
    createProxyMiddleware(
      '/ws/',
      {
        target: `ws://${host}`,
        changeOrigin: true,
        xfwd: false,
        ws: true,
      },
    ),
  );
};