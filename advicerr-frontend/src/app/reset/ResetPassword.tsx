"use client"
import React, { useState } from "react";
import { useRouter } from 'next/navigation';
import {
  Alert, AlertIcon,
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  Heading,
  VStack,
  useToast,
  HStack,
  PinInput,
  PinInputField,
  Text,
} from "@chakra-ui/react";
import { useSendCodeToEmailMutation, useSendCodeToCheckMutation, useSendNewPasswordMutation } from "../store/apis/passwordRecoverApi"; 
import usePrefixedTranslation from '@/app/hooks/usePrefixedTranslation';


const ResetPassword = () => {
  const { t } = usePrefixedTranslation('Pages.ResetPasswordPage');
  const router = useRouter();
  const [step, setStep] = useState(1); // Step 1: Enter email, Step 2: Enter Code, Step 3: Reset Password
  const [email, setEmail] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [passwordError, setPasswordError] = React.useState<string | null>(null);
  

  const [error, setError] = useState<string | null>(null);

  const toast = useToast();

  // API Calls
  const [sendCodeToEmail, { isLoading: sendingCode }] = useSendCodeToEmailMutation();
  const [sendCodeToCheck, { isLoading: verifyingCode }] = useSendCodeToCheckMutation();
  const [sendNewPassword, { isLoading: resettingPassword }] = useSendNewPasswordMutation();


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


  // Step 1: Handle Email Submission
const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await sendCodeToEmail({ email }).unwrap();  // Call API
      toast({
        title: t("codeSentLabel"),
        description: t("codeSentDescription") + `{email}.`,
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      setStep(2); // Move to Step 2
    } catch (error) {
      toast({
        title: t("errorLabel"),
        description: t("failedToSendCodeLabel"),
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };
  
  // Step 2: Handle Code Verification
  const handleCodeSubmit = async () => {
    try {
      await sendCodeToCheck({ email, code: verificationCode }).unwrap();  // Call API
      toast({
        title: t("codeVerifiedLabel"),
        description: t("codeVerifiedDescription"),
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      setStep(3); // Move to Step 3
    } catch (error) {
      toast({
        title: t("invalidCodeLabel"),
        description: t("invalidCodeDescription"),
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };
  
  // Step 3: Handle Password Reset
  const handlePasswordReset = async (e: React.FormEvent) => {
    e.preventDefault();

    
    if (newPassword !== confirmPassword) {
      toast({
        title: t("errorLabel"),
        description: t("passwordsNotMatchingLabel"),
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    try {
      const isPasswordValid = validatePassword(newPassword);
      if (!isPasswordValid){
        toast({
        title: t("erorLabel"),
        description: t("passwordLengthLabel"),
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
        return;
      }
      await sendNewPassword({ email, password: newPassword }).unwrap();  // Call API
      toast({
        title: t("passwordUpdatedLabel"),
        description: t("passwordUpdatedDescription"),
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      router.push("/login")
      // Reset form & redirect to login page
      setStep(1);
      setEmail("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (error) {
      toast({
        title: t("erorLabel"),
        description: t("failedToSendCodeLabel"),
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  return (
    <Box maxW="lg" mx="auto" mt={10} p={8} borderWidth={1} borderRadius="lg" boxShadow="xl">
      <Heading as="h2" size="lg" textAlign="center" mb={6}>
        {step === 1 && t("forgotPasswordStepLabel")}
        {step === 2 && t("enterCodeStepLabel")}
        {step === 3 && t("setNewPasswordLabel")}
      </Heading>

      <VStack spacing={6}>
        {step === 1 && (
        <form onSubmit={handleEmailSubmit}>
          <FormControl id="email" isRequired>
            <FormLabel>{t("emailLabel")}</FormLabel>
            <Input
              type="email"
              placeholder={t("emailPlaceholder")}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              />
            <Button colorScheme="teal" size="lg" width="full" mt={4} type="submit" isLoading={sendingCode}>
              {t("sendVerifCodeButtonLabel")}
            </Button>
            {/* <Button colorScheme="teal" size="lg" width="full" mt={4}>
              Send Verification Code
              </Button> */}
          </FormControl>
        </form>
        )
      }
      {error && (
        <Alert status="error">
          <AlertIcon />
          {error}
        </Alert>
        )}
        
        {step === 2 && (
          <>
            <Text>{t("enterCodeInputLabel")}</Text>
            <HStack>
              <PinInput
                otp
                value={verificationCode}
                onChange={(value) => setVerificationCode(value)}
              >
                <PinInputField />
                <PinInputField />
                <PinInputField />
                <PinInputField />
                <PinInputField />
                <PinInputField />
              </PinInput>
            </HStack>
            <Button colorScheme="teal" size="lg" width="full" mt={4} onClick={handleCodeSubmit} isLoading={verifyingCode}>
              {t("verifyButtonLabel")}
            </Button>
            {/* <Button colorScheme="teal" size="lg" width="full" mt={4}>
              Verify Code
            </Button> */}
          </>
        )}

        {step === 3 && (
          <>
            <FormControl isRequired>
              <FormLabel>{t("newPasswordInputLabel")}</FormLabel>
              <Input
                type="password"
                placeholder={t("newPasswordPlaceholder")}
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
              />
            </FormControl>
            <FormControl isRequired>
              <FormLabel>{t("confirmPasswordInputLabel")}</FormLabel>
              <Input
                type="password"
                placeholder={t("confirmPasswordPlaceholder")}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </FormControl>
            <Button colorScheme="teal" size="lg" width="full" mt={4} onClick={handlePasswordReset} isLoading={resettingPassword}>
              {t("changePasswordButtonLabel")}
            </Button>
            {/* <Button colorScheme="teal" size="lg" width="full" mt={4}>
              Change Password
            </Button> */}
          </>
        )}
      </VStack>
    </Box>
  );
};

export default ResetPassword;
