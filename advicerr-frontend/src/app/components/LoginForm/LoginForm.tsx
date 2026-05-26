"use client"
import React from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation'
import Cookies from 'js-cookie';

import { Alert, AlertIcon, Box, Button, FormControl, FormLabel, Input, VStack, Heading, Text, FormErrorMessage } from '@chakra-ui/react';

import { useLoginUserMutation } from '@/app/store/apis/usersApi';

import usePrefixedTranslation from '@/app/hooks/usePrefixedTranslation';

const LoginForm = () => {
  const { t } = usePrefixedTranslation('Components.LoginForm');
  const [loginUser, { data, isSuccess, isLoading }] = useLoginUserMutation();
  const router = useRouter();
  const searchParams = useSearchParams();

  // Form state
  const [email, setEmail] = React.useState(searchParams.get('email') ?? '');
  const [password, setPassword] = React.useState('');
  const [error, setError] = React.useState<string | null>(null);
  const infoMessage = searchParams.get('after_order') === 'true'
    ? 'Заявку створено. Увійдіть у систему, щоб відстежувати статус консультації.'
    : null;


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    try {
      const response = await loginUser(formData).unwrap();
      console.log('Login successful:', response);
    } catch (err: any) {
      console.error('Login failed:', err);
      setError(err.data?.message || t('loginErrorLabel'));
    }
  };

  React.useEffect(() => {
    if (isSuccess && data?.access_token && data?.refresh_token) {
      console.log('Login successful:', data);
      // This should be used with https
      // Cookies.set('access_token', data.access_token, { secure: true });
      // Cookies.set('refresh_token', data.refresh_token, { secure: true });
      // This should be used without https
      Cookies.set('access_token', data.access_token);
      Cookies.set('refresh_token', data.refresh_token);

      router.push('/dashboard'); // Redirect to dashboard
    }
  }, [isSuccess, data, router]);

  return (
    <Box
      borderWidth="1px"
      borderRadius="lg"
      overflow="hidden"
      p={6}
      maxW="md"
      mx="auto"
      mt={10}
      boxShadow="xl"
    >
      <Heading as="h1" size="lg" textAlign="center" mb={6}>
        {t("logInLabel")}
      </Heading>
      <form onSubmit={handleSubmit}>
        <VStack spacing={4}>
          <FormControl id="email" isRequired >
            <FormLabel>{t("emailLabel")}</FormLabel>
            <Input
              type="email"
              placeholder={t("emailInputPlaceholder")}
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
              }}
            />
          </FormControl>

          <FormControl id="password" isRequired>
            <FormLabel>{t("passwordLabel")}</FormLabel>
            <Input
              type="password"
              placeholder={t("passwordInputPlaceholder")}
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
              }}
            />
          </FormControl>

          {error && (
            <Alert status="error">
              <AlertIcon />
              {error}
            </Alert>
          )}

          {infoMessage && (
            <Alert status="info">
              <AlertIcon />
              {infoMessage}
            </Alert>
          )}

          <Button colorScheme="teal" size="lg" width="full" type="submit" isLoading={isLoading}>
            {t("logInButtonLabel")}
          </Button>
        </VStack>
      </form>
      {/* <Text textAlign="center" mt={4}>
        {t("alternativeOptionLabel")} <Button variant="link" colorScheme="teal"><Link href={"/signup"}>{t("registerLabel")}</Link></Button>
      </Text> */}
      <Text textAlign="center" mt={4}>
        {t("forgotPasswordLabel")} <Button variant="link" colorScheme="teal"><Link href={"/reset"}>{t("recoverPasswordLabel")}</Link></Button>
      </Text>
    </Box>
  );
};

export default LoginForm;
