import React from 'react';
import { Box, Spinner, Text, VStack } from '@chakra-ui/react';

type Props = {
  message: string;
  variant: "loading" | "error" | "empty";
  size?: "page" | "section";
};

const StatusState = ({ message, variant, size = "page" }: Props) => {
  const minHeight = size === "page" ? "50vh" : "220px";

  return (
    <Box display="flex" alignItems="center" justifyContent="center" minH={minHeight} w="full">
      <VStack spacing={4}>
        {variant === "loading" && <Spinner size="xl" color="teal.500" />}
        <Text color={variant === "error" ? "red.500" : "gray.600"} fontSize="lg" textAlign="center">
          {message}
        </Text>
      </VStack>
    </Box>
  );
};

export default StatusState;
