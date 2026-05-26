// "use client"
import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Alert, AlertIcon, Box, Button, FormControl, FormLabel, Input, VStack, Heading, Text, FormErrorMessage } from '@chakra-ui/react';

import { useRegisterUserMutation } from '@/app/store/apis/usersApi';
import { apiBaseUrl, describeApiError, resolveApiUrl } from '@/app/store/apis/apiClient';

import usePrefixedTranslation from '@/app/hooks/usePrefixedTranslation';

const SignUpForm = () => {
  const { t } = usePrefixedTranslation('Components.SignupForm');
  const [registerUser, { isLoading }] = useRegisterUserMutation();
  const router = useRouter();

  const [firstName, setFirstName] = React.useState('');
  const [lastName, setLastName] = React.useState('');
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [error, setError] = React.useState<string | null>(null);


  // Validation state
  const [emailError, setEmailError] = React.useState<string | null>(null);
  const [passwordError, setPasswordError] = React.useState<string | null>(null);
  const signupUrl = resolveApiUrl('auth/signup');

  const validateEmail = (value: string) => {
    if (!value.trim()) {
      setEmailError(t("emailRequiredLabel"));
      return false;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      setEmailError(t("emailInvalidLabel"));
      return false;
    }
    setEmailError(null);
    return true;
  };

  const validatePassword = (value: string) => {
    if (!value.trim()) {
      setPasswordError(t("passwordRequiredLabel"));
      return false;
    }
    // Ensure at least 8 characters, containing at least 1 letter and 1 number
    const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;
    if (!passwordRegex.test(value)) {
      setPasswordError(t("passwordLengthLabel"));  // Ensure this key exists in translations
      return false;
    }
    setPasswordError(null);
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validate fields before submission
    const isEmailValid = validateEmail(email);
    const isPasswordValid = validatePassword(password);

    if (!isEmailValid || !isPasswordValid) {
      return;
    }

    try {
      console.info('Signup request target:', signupUrl, 'base URL:', apiBaseUrl);
      // Send registration request
      await registerUser({ first_name: firstName, last_name: lastName, email, password }).unwrap();

      // Redirect on success
      router.push('/login');
    } catch (err: unknown) {
      console.error('Registration failed:', err);
      setError(describeApiError(err, 'auth/signup'));
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
      <Heading as="h1" size="lg" textAlign="center" mb={6}>
        {t("signUpLabel")}
      </Heading>
      <form onSubmit={handleSubmit}>
        <VStack spacing={4}>
          <FormControl id="name" isRequired>
            <FormLabel>{t("nameLabel")}</FormLabel>
            <Input type="text" placeholder={t("nameInputPlaceholder")} value={firstName} onChange={(e) => setFirstName(e.target.value)}/>
          </FormControl>
          <FormControl id="surname" isRequired>
            <FormLabel>{t("surnameLabel")}</FormLabel>
            <Input type="text" placeholder={t("surnameInputPlaceholder")} value={lastName} onChange={(e) => setLastName(e.target.value)}/>
          </FormControl>
          <FormControl id="email" isRequired isInvalid={!!emailError}>
            <FormLabel>{t("emailLabel")}</FormLabel>
            <Input type="email" placeholder={t("emailInputPlaceholder")} value={email} onChange={(e) => setEmail(e.target.value)} onBlur={() => validateEmail(email)}/>
            {emailError && <FormErrorMessage>{emailError}</FormErrorMessage>}
          </FormControl>
          <FormControl id="password" isRequired isInvalid={!!passwordError}>
            <FormLabel>{t("passwordLabel")}</FormLabel>
            <Input type="password" placeholder={t("passwordInputPlaceholder")} value={password} onChange={(e) => setPassword(e.target.value)} onBlur={() => validatePassword(password)}/>
            {passwordError && <FormErrorMessage>{passwordError}</FormErrorMessage>}
          </FormControl>
          {error && (
            <Alert status="error" borderRadius="md">
              <AlertIcon />
              {error}
            </Alert>
          )}
          {process.env.NODE_ENV !== 'production' && (
            <Text fontSize="sm" color="gray.500" textAlign="center">
              Signup request target: {signupUrl}
            </Text>
          )}
          <Button colorScheme="teal" size="lg" width="full" type="submit" isLoading={isLoading}>
            {t("signUpButtonLabel")}
          </Button>
        </VStack>
      </form>
      <Text textAlign="center" mt={4}>
        {t("alternativeOptionLabel")} <Button variant="link" colorScheme="teal"><Link href={"/login"}>{t("loginLabel")}</Link></Button>
      </Text>
    </Box>
  );
};

export default SignUpForm;
