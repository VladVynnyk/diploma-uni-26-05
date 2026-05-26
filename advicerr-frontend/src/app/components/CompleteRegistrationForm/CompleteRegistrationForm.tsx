"use client"
import React from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import Cookies from 'js-cookie';
import {
  Alert,
  AlertIcon,
  Box,
  Button,
  FormControl,
  FormErrorMessage,
  FormLabel,
  Heading,
  Input,
  Text,
  VStack,
} from '@chakra-ui/react';

import { useCompleteRegistrationMutation } from '@/app/store/apis/usersApi';
import { describeApiError } from '@/app/store/apis/apiClient';

const PASSWORD_REGEX = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;

const CompleteRegistrationForm = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const email = searchParams.get('email') ?? '';

  const [completeRegistration, { isLoading }] = useCompleteRegistrationMutation();

  const [password, setPassword] = React.useState('');
  const [confirmPassword, setConfirmPassword] = React.useState('');
  const [passwordError, setPasswordError] = React.useState<string | null>(null);
  const [confirmPasswordError, setConfirmPasswordError] = React.useState<string | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [showLoginLink, setShowLoginLink] = React.useState(false);

  const validatePassword = (value: string) => {
    if (!value.trim()) {
      setPasswordError('Потрібен пароль.');
      return false;
    }

    if (!PASSWORD_REGEX.test(value)) {
      setPasswordError('Пароль має мати не менше, ніж 8 символів, 1 цифру та 1 букву.');
      return false;
    }

    setPasswordError(null);
    return true;
  };

  const validateConfirmPassword = (value: string, currentPassword: string) => {
    if (!value.trim()) {
      setConfirmPasswordError('Потрібно підтвердити пароль.');
      return false;
    }

    if (value !== currentPassword) {
      setConfirmPasswordError('Паролі не збігаються.');
      return false;
    }

    setConfirmPasswordError(null);
    return true;
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setShowLoginLink(false);

    if (!email) {
      setError('Не вказано email для завершення реєстрації.');
      return;
    }

    const isPasswordValid = validatePassword(password);
    const isConfirmPasswordValid = validateConfirmPassword(confirmPassword, password);

    if (!isPasswordValid || !isConfirmPasswordValid) {
      return;
    }

    try {
      const tokens = await completeRegistration({
        email,
        password,
        confirm_password: confirmPassword,
      }).unwrap();

      Cookies.set('access_token', tokens.access_token);
      Cookies.set('refresh_token', tokens.refresh_token);
      router.push('/dashboard');
    } catch (requestError: unknown) {
      const nextError = describeApiError(requestError, 'auth/complete-registration');
      setError(nextError);
      setShowLoginLink(nextError.includes('зареєстрований'));
    }
  };

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
      <Heading as="h1" size="lg" textAlign="center" mb={4}>
        Завершення реєстрації
      </Heading>

      <Text color="gray.600" textAlign="center" mb={6}>
        Заявку на консультацію створено. Створіть пароль, щоб увійти в особистий кабінет і відстежувати статус консультації.
      </Text>

      <form onSubmit={handleSubmit}>
        <VStack spacing={4}>
          <FormControl isRequired>
            <FormLabel>Ел-пошта</FormLabel>
            <Input type="email" value={email} isDisabled placeholder="Введіть ел-пошту" />
          </FormControl>

          <FormControl isRequired isInvalid={!!passwordError}>
            <FormLabel>Пароль</FormLabel>
            <Input
              type="password"
              value={password}
              placeholder="Введіть пароль"
              onChange={(e) => {
                setPassword(e.target.value);
                if (passwordError) {
                  validatePassword(e.target.value);
                }
              }}
              onBlur={() => validatePassword(password)}
            />
            {passwordError && <FormErrorMessage>{passwordError}</FormErrorMessage>}
          </FormControl>

          <FormControl isRequired isInvalid={!!confirmPasswordError}>
            <FormLabel>Підтвердіть пароль</FormLabel>
            <Input
              type="password"
              value={confirmPassword}
              placeholder="Повторіть пароль"
              onChange={(e) => {
                setConfirmPassword(e.target.value);
                if (confirmPasswordError) {
                  validateConfirmPassword(e.target.value, password);
                }
              }}
              onBlur={() => validateConfirmPassword(confirmPassword, password)}
            />
            {confirmPasswordError && <FormErrorMessage>{confirmPasswordError}</FormErrorMessage>}
          </FormControl>

          {error && (
            <Alert status="error" borderRadius="md">
              <AlertIcon />
              <Text>{error}</Text>
            </Alert>
          )}

          {showLoginLink && (
            <Text textAlign="center">
              <Button as={Link} href={`/login?email=${encodeURIComponent(email)}`} variant="link" colorScheme="teal">
                Увійти
              </Button>
            </Text>
          )}

          <Button colorScheme="teal" size="lg" width="full" type="submit" isLoading={isLoading}>
            Завершити реєстрацію
          </Button>
        </VStack>
      </form>
    </Box>
  );
};

export default CompleteRegistrationForm;
