"use client"
import React, { useState } from 'react';
import {
  FormControl, FormLabel,
  Box, VStack, Button, Heading, Input, Avatar, Textarea, Switch, useToast, FormErrorMessage
} from '@chakra-ui/react';

import TagSelector from '@/app/components/TagSelector/TagSelector';

import { validateEmail, validatePhoneNumber } from '@/app/utils/validation';

import { useUpdateUserMutation } from '@/app/store/apis/usersApi';

import usePrefixedTranslation from '@/app/hooks/usePrefixedTranslation';

import { TTagForUpdate } from '@/app/types/TagTypes';
import ImageUploader from '@/app/components/ImageUploader/ImageUploader';

const MAX_PRICE = 2147483647;
const PRICE_REQUIRED_MESSAGE = "Будь ласка, вкажіть вартість.";
const PRICE_WHOLE_NUMBER_MESSAGE = "Будь ласка, вкажіть вартість без літер і дробів.";
const PRICE_INVALID_MESSAGE = "Будь ласка, вкажіть коректну вартість.";
const PRICE_TOO_HIGH_MESSAGE = "Сума занадто велика. Вкажіть меншу вартість.";
const PHONE_REQUIRED_MESSAGE = "Будь ласка, вкажіть номер телефону.";

const getPriceValidationError = (rawPrice: string, isConsultant: boolean) => {
  if (!isConsultant) {
    return null;
  }

  const trimmedPrice = rawPrice.trim();

  if (!trimmedPrice) {
    return PRICE_REQUIRED_MESSAGE;
  }

  if (!/^\d+$/.test(trimmedPrice)) {
    return PRICE_WHOLE_NUMBER_MESSAGE;
  }

  const numericPrice = Number(trimmedPrice);

  if (!Number.isSafeInteger(numericPrice) || numericPrice < 0) {
    return PRICE_INVALID_MESSAGE;
  }

  if (numericPrice > MAX_PRICE) {
    return PRICE_TOO_HIGH_MESSAGE;
  }

  return null;
};

const getUpdateErrorMessage = (error: any, t: (key: string) => string) => {
  const detail = String(error?.data?.detail || error?.error || "").toLowerCase();

  if (detail.includes("invalid input syntax for type integer")) {
    return PRICE_INVALID_MESSAGE;
  }

  if (detail.includes("out of range for type integer") || detail.includes("numericvalueoutofrange")) {
    return PRICE_TOO_HIGH_MESSAGE;
  }

  if (detail.includes("phone number is required")) {
    return PHONE_REQUIRED_MESSAGE;
  }

  return t("failedToUpdateInfoLabel");
};

type TReview = {
  client_id: string,
  consultant_id: string,
  created_at: string,
  description: string,
  id: string,
  rating: number
}

type TCurrentUser = {
  email: string,
  description: string,
  created_at: string,
  first_name: string,
  id: string,
  is_admin?: boolean,
  is_consultant: boolean,
  last_name: string,
  phone_number?: string,
  photo?: string,
  price: number,
  reviews_as_consultant: Array<TReview>,
  tags: Array<TTagForUpdate>
}

const PersonalInformation = ({ props }: {props: TCurrentUser}) => {
    const { t } = usePrefixedTranslation('Pages.DashboardPage.personalInfo');

    const [name, setName] = useState(props.first_name);
    const [surname, setSurname] = useState(props.last_name);
    const [photo, setPhoto] = useState(props.photo || 'https://via.placeholder.com/150');
    const [description, setDescription] = useState(props.description || "");
    const [email, setEmail] = useState(props.email);
    const [phone, setPhone] = useState(props.phone_number || "");
    const [showOnWebsite, setShowOnWebsite] = useState(props.is_consultant);
    const [price, setPrice] = useState(String(props.price ?? 0));
    const [tags, setTags] = useState(props.tags);

    const toast = useToast();

    const [emailError, setEmailError] = React.useState<string | null>(null);
    const [phoneNumberError, setPhoneNumberError] = React.useState<string | null>(null);
    const [priceError, setPriceError] = React.useState<string | null>(null);
    const [isCropping, setIsCropping] = useState(false);

    const id = props.id

    const [updateUser] = useUpdateUserMutation();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        const isValidEmail = validateEmail(email, setEmailError, t)
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

        if (!phone.trim()) {
          setPhoneNumberError(PHONE_REQUIRED_MESSAGE);
          toast({
            title: t("errorToastLabel"),
            description: PHONE_REQUIRED_MESSAGE,
            status: "error",
            duration: 3000,
            isClosable: true,
          });
          return;
        }

        const isValidPhoneNumber = validatePhoneNumber(phone, setPhoneNumberError, t)
        if (!isValidPhoneNumber) {
          toast({
            title: t("errorToastLabel"),
            description: t("phoneInvalidInputError"),
            status: "error",
            duration: 3000,
            isClosable: true,
          })
          return;
        }

        const currentPriceError = getPriceValidationError(price, showOnWebsite);
        setPriceError(currentPriceError);

        if (currentPriceError) {
          toast({
            title: t("errorToastLabel"),
            description: currentPriceError,
            status: "error",
            duration: 3000,
            isClosable: true,
          })
          return;
        }

        const body = {
          first_name: name,
          last_name: surname,
          tags,
          phone_number: phone.trim(),
          photo,
          description,
          price: showOnWebsite ? price.trim() : "0",
          email,
          is_consultant: showOnWebsite,
        };

        try {
          await updateUser({ id, body }).unwrap();
          toast({
            title: t("successToastLabel"),
            description: t("personalInfoUpdatedSuccessfullyLabel"),
            status: "success",
            duration: 3000,
            isClosable: true,
          });
        } catch (err: any) {
          toast({
            title: t("errorToastLabel"),
            description: getUpdateErrorMessage(err, t),
            status: "error",
            duration: 3000,
            isClosable: true,
          });
        }
      };

    if (props == undefined) return <div>Error: data is undefined</div>

    return (
      <Box>
        <Heading as="h2" size="xl" mb={4}>
          {t("personalInformationLabel")}
        </Heading>
        {isCropping ? (
              <ImageUploader id={id} setIsCropping={setIsCropping} />
            ) : (
        <form onSubmit={handleSubmit}>
          <VStack spacing={4} align="stretch">
            <Avatar size="xl" src={photo} />
            <Button onClick={() => setIsCropping(true)}>{t("changePhotoButtonLabel")}</Button>
            <FormControl>
              <FormLabel>{t("nameLabel")}</FormLabel>
              <Input value={name} onChange={(e) => setName(e.target.value)} />
            </FormControl>
            <FormControl>
              <FormLabel>{t("surnameLabel")}</FormLabel>
              <Input value={surname} onChange={(e) => setSurname(e.target.value)} />
            </FormControl>
            <FormControl display="flex" alignItems="center">
              <FormLabel mb="0">{t("showOnWebsiteLabel")}</FormLabel>
              <Switch isChecked={showOnWebsite} onChange={(e) => setShowOnWebsite(e.target.checked)} />
            </FormControl>
            {showOnWebsite && (
              <>
                <FormControl>
                  <FormLabel>{t("descriptionLabel")}</FormLabel>
                  <Textarea value={description} onChange={(e) => setDescription(e.target.value)} />
                </FormControl>
                <FormControl isInvalid={!!priceError}>
                  <FormLabel>{t("priceLabel")}</FormLabel>
                  <Input
                    type="number"
                    min={0}
                    max={MAX_PRICE}
                    value={price}
                    onChange={(e) => {
                      setPrice(e.target.value);
                      if (priceError) {
                        setPriceError(getPriceValidationError(e.target.value, true));
                      }
                    }}
                  />
                  {priceError && <FormErrorMessage>{priceError}</FormErrorMessage>}
                </FormControl>
                <TagSelector tags={tags} setTags={setTags}/>
              </>
            )}
            <FormControl>
              <FormLabel>{t("emailLabel")}</FormLabel>
              <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </FormControl>
            <FormControl isRequired isInvalid={!!phoneNumberError}>
              <FormLabel>{t("phone")}</FormLabel>
              <Input
                value={phone}
                onChange={(e) => {
                  setPhone(e.target.value);
                  if (phoneNumberError && e.target.value.trim()) {
                    setPhoneNumberError(null);
                  }
                }}
              />
              {phoneNumberError && <FormErrorMessage>{phoneNumberError}</FormErrorMessage>}
            </FormControl>
            <Button type="submit" colorScheme="teal" size="lg">
              {t("saveButtonLabel")}
            </Button>
          </VStack>
        </form>
      )}
      </Box>
    );
};

export default PersonalInformation
