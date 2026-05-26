import React from 'react'
import { useRouter } from 'next/navigation';
import { Box, Button, FormControl, FormErrorMessage, FormLabel, Input, Textarea, VStack, Heading, useToast } from '@chakra-ui/react';

import Cookies from "js-cookie";
import { useCreateOrderMutation } from '@/app/store/apis/ordersApi';

import { validateEmail, validatePhoneNumber } from '@/app/utils/validation';

import usePrefixedTranslation from '@/app/hooks/usePrefixedTranslation';

import { TLoggedInUser } from '@/app/types/UserTypes';

type Props = {
  consultantId: string,
  price: number
}

const OrderForm = ({consultantId, price}: Props) => {
  const { t } = usePrefixedTranslation('Components.OrderForm')
  const router = useRouter();

  const toast = useToast();
  const [createOrder, { isLoading }] = useCreateOrderMutation();

  const [firstName, setFirstName] = React.useState("");
  const [lastName, setLastName] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [phoneNumber, setPhoneNumber] = React.useState("");
  const [topic, setTopic] = React.useState("");
  const [message, setMessage] = React.useState("");
  const [scheduledAt, setScheduledAt] = React.useState("");
  const [durationMinutes, setDurationMinutes] = React.useState("60");

  const [emailError, setEmailError] = React.useState<string | null>(null);
  const [phoneNumberError, setPhoneNumberError] = React.useState<string | null>(null);
  const [topicError, setTopicError] = React.useState<string | null>(null);

  const [isLoggedIn, setIsLoggedIn] = React.useState(false);

  React.useEffect(() => {
    const accessToken = Cookies.get("access_token") || "";
    if (accessToken) {
      setIsLoggedIn(true);
    }
  }, []);

  const extractErrorMessage = (error: unknown) => {
    if (
      error &&
      typeof error === "object" &&
      "data" in error &&
      error.data &&
      typeof error.data === "object" &&
      "detail" in error.data &&
      typeof error.data.detail === "string"
    ) {
      return error.data.detail;
    }

    return t("failedToSubmitLabel");
  };

  const validateConsultationFields = () => {
    if (!topic.trim()) {
      const nextError = "Будь ласка, коротко вкажіть тему консультації.";
      setTopicError(nextError);
      toast({
        title: t("errorToastLabel"),
        description: nextError,
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return false;
    }

    setTopicError(null);

    const parsedDuration = Number(durationMinutes);
    if (!Number.isInteger(parsedDuration) || parsedDuration <= 0) {
      toast({
        title: t("errorToastLabel"),
        description: "Будь ласка, вкажіть тривалість консультації в хвилинах.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return false;
    }

    return true;
  };

  const getConsultationPayload = () => ({
    consultant_id: consultantId,
    price,
    topic: topic.trim(),
    message: message.trim(),
    scheduled_at: scheduledAt ? new Date(scheduledAt).toISOString() : null,
    duration_minutes: Number(durationMinutes),
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateConsultationFields()) {
      return;
    }

    try {
      let requestBody;

      if (isLoggedIn) {
        const storedUser = localStorage.getItem('currentUser') || "";
        const userObject: TLoggedInUser = JSON.parse(storedUser);

        if (userObject.id === consultantId) {
          toast({
            title: t("errorToastLabel"),
            description: "Ви не можете замовити консультацію у себе.",
            status: "error",
            duration: 3000,
            isClosable: true,
          });
          return;
        }

        requestBody = {
          consultation: {
            ...getConsultationPayload(),
            client_id: userObject.id,
          },
        };
      } else {
        if (!firstName || !lastName || !phoneNumber || !email) {
          toast({
            title: t("errorToastLabel"),
            description: t("allFieldsAreRequiredToastLabel"),
            status: "error",
            duration: 3000,
            isClosable: true,
          });
          return;
        }

        const isValidEmail = validateEmail(email, setEmailError, t)
        const isValidPhone = validatePhoneNumber(phoneNumber, setPhoneNumberError, t)

        if (!isValidEmail) {
          toast({
            title: t("errorToastLabel"),
            description: t("emailInvalidInputError"),
            status: "error",
            duration: 3000,
            isClosable: true,
          });
          return;
        }

        if (!isValidPhone) {
          toast({
            title: t("errorToastLabel"),
            description: t("phoneInvalidInputError"),
            status: "error",
            duration: 3000,
            isClosable: true,
          })
          return;
        }

        requestBody = {
          consultation: {
            ...getConsultationPayload(),
            first_name: firstName,
            last_name: lastName,
            phone_number: phoneNumber,
            email,
          },
        };
      }

      const response = await createOrder(requestBody).unwrap();

      if (!isLoggedIn && response.auth_flow.should_login && response.auth_flow.email) {
        toast({
          title: t("successToastLabel"),
          description: response.auth_flow.message ?? "Заявку створено. Увійдіть у систему, щоб відстежувати статус консультації.",
          status: "success",
          duration: 3000,
          isClosable: true,
        });
        router.push(`/login?email=${encodeURIComponent(response.auth_flow.email)}&after_order=true`);
        return;
      }

      if (!isLoggedIn && response.auth_flow.requires_complete_registration && response.auth_flow.email) {
        toast({
          title: t("successToastLabel"),
          description: response.auth_flow.message ?? "Заявку створено. Завершіть реєстрацію, щоб увійти в кабінет.",
          status: "success",
          duration: 3000,
          isClosable: true,
        });
        router.push(`/complete-registration?email=${encodeURIComponent(response.auth_flow.email)}`);
        return;
      }

      toast({
        title: t("successToastLabel"),
        description: "Запит на консультацію успішно надіслано.",
        status: "success",
        duration: 3000,
        isClosable: true,
      });

      setTopic("");
      setMessage("");
      setScheduledAt("");
      setDurationMinutes("60");

      if (!isLoggedIn) {
        setFirstName("");
        setLastName("");
        setEmail("");
        setPhoneNumber("");
      }
    } catch (error) {
      toast({
        title: t("errorToastLabel"),
        description: extractErrorMessage(error),
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  return (
    <Box borderWidth="1px" borderRadius="lg" overflow="hidden" p={6} maxW="md" mx="auto" mt={10} boxShadow="xl">
      <Heading as="h2" size="lg" textAlign="center" mb={6}>
        {t("headingLabel")}
      </Heading>

      <form onSubmit={handleSubmit}>
        <VStack spacing={4}>
          {!isLoggedIn && (
            <>
              <FormControl isRequired>
                <FormLabel>{t("nameLabel")}</FormLabel>
                <Input placeholder={t("nameInputPlaceholder")} value={firstName} onChange={(e) => setFirstName(e.target.value)} />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>{t("surnameLabel")}</FormLabel>
                <Input placeholder={t("surnameInputPlaceholder")} value={lastName} onChange={(e) => setLastName(e.target.value)} />
              </FormControl>

              <FormControl id="email" isRequired isInvalid={!!emailError}>
                <FormLabel>{t("emailLabel")}</FormLabel>
                <Input type="email" placeholder={t("emailInputPlaceholder")} value={email} onChange={(e) => setEmail(e.target.value)} />
                {emailError && <FormErrorMessage>{emailError}</FormErrorMessage>}
              </FormControl>

              <FormControl id="tel" isRequired isInvalid={!!phoneNumberError}>
                <FormLabel>{t("phoneLabel")}</FormLabel>
                <Input type="tel" placeholder={t("phoneInputPlaceholder")} value={phoneNumber} onChange={(e) => setPhoneNumber(e.target.value)} />
                {phoneNumberError && <FormErrorMessage>{phoneNumberError}</FormErrorMessage>}
              </FormControl>
            </>
          )}

          <FormControl isRequired isInvalid={!!topicError}>
            <FormLabel>Тема консультації</FormLabel>
            <Input
              placeholder="Наприклад: кар'єра, маркетинг, запуск бізнесу"
              value={topic}
              onChange={(e) => {
                setTopic(e.target.value);
                if (e.target.value.trim()) {
                  setTopicError(null);
                }
              }}
            />
            {topicError && <FormErrorMessage>{topicError}</FormErrorMessage>}
          </FormControl>

          <FormControl>
            <FormLabel>Що ви хочете обговорити</FormLabel>
            <Textarea
              placeholder="Коротко опишіть ваш запит, щоб консультант міг підготуватися."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
          </FormControl>

          <FormControl>
            <FormLabel>Бажана дата та час</FormLabel>
            <Input
              type="datetime-local"
              value={scheduledAt}
              onChange={(e) => setScheduledAt(e.target.value)}
            />
          </FormControl>

          <FormControl>
            <FormLabel>Тривалість, хв</FormLabel>
            <Input
              type="number"
              min={1}
              value={durationMinutes}
              onChange={(e) => setDurationMinutes(e.target.value)}
            />
          </FormControl>

          <Button colorScheme="teal" size="lg" width="full" type="submit" isLoading={isLoading}>
            {isLoggedIn ? t("loggedInSubmitButtonLabel") : t("unLoggedSubmitButtonLabel")}
          </Button>
        </VStack>
      </form>
    </Box>
  );
};

export default OrderForm;
