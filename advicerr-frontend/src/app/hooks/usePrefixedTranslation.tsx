import { useTranslation as originalUseTranslation } from 'react-i18next';

const usePrefixedTranslation = (translationNamespace?: string) => {
  const { t } = originalUseTranslation();

  const prefixedT = (key: string, options?: any): string => {
    const translationKey = key[0]===`.` ?
      key.slice(1) :
      (translationNamespace ? `${translationNamespace}.${key}` : key);

    return t(translationKey, options) as string;
  };

  return { t: prefixedT };
};

export default usePrefixedTranslation;