"use client"
import React from 'react';
import { Flex,
  Box, VStack, HStack, Button, Heading, Input
} from '@chakra-ui/react';
import { ArrowBackIcon } from '@chakra-ui/icons';
import { TPayment } from '@/app/types/PaymentTypes';

import usePrefixedTranslation from '../../hooks/usePrefixedTranslation'


type TGoBack = () => void;

type PaymentProps = {
  payment: TPayment | null,
  goBack?: TGoBack,
  isMobile?: boolean
}

const Payment = ({ payment, goBack, isMobile }: PaymentProps) => {
  const { t } = usePrefixedTranslation('Components.PayButton');

  if (!payment) {
    return <div>Unexpected error</div>;
  }
  
  return (
    <Box h="90%" display="flex" flexDirection="column">
      {goBack && (
        <Button
          leftIcon={<ArrowBackIcon />}
          onClick={goBack}
          mb={4}
          colorScheme="teal"
        >
          Go back to main
        </Button>
      )}
    <Heading as="h3" size="lg" mb={4}>
        {payment.name}
    </Heading>
      {/* <VStack spacing={4} align="stretch" flex="1" overflowY="auto"> */}
      {/* </VStack> */}
      <Box p={4} bg="white" boxShadow="sm" display="flex" justifyContent="center">
        <HStack spacing={4}>
          <Button colorScheme="teal" width="15rem">{t("payLabel")}</Button>
        </HStack>
      </Box>
    </Box>
  )
};

export default Payment