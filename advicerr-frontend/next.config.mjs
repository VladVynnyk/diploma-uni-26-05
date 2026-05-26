/** @type {import('next').NextConfig} */




const nextConfig = {
    output: "standalone",
    i18n: {
        locales: ['uk', 'ru'], // List of supported locales
        defaultLocale: "uk",         // Default language
        localeDetection: true,       // Auto-detect user's locale
      },
  };

export default nextConfig;
