import React from 'react'
import { Box, VStack, HStack, Avatar } from "@chakra-ui/react";
import { StarIcon } from '@chakra-ui/icons';

import usePrefixedTranslation from '../../hooks/usePrefixedTranslation'

type Props = {
    name: string,
    surname: string, 
    description: string,
    score: number,
    isMobile: boolean
}

const SingleReview = ({name, surname, description, score, isMobile}: Props) => {
  const { t } = usePrefixedTranslation('Components.Review');
 
  return (
    <Box
        as='div'
        bg="white"
        boxShadow="md"
        borderRadius="md"
        p={4}
        border="1px solid"
        borderColor="gray.200"
        w="full"
        maxW="sm"
        _hover={{ boxShadow: "lg" }}
      >
        <HStack spacing={4} align="center">
          {/* Avatar */}
          <Avatar name={name} />
          <VStack align="start" spacing={0} flex="1">
            {/* Name */}
            <Box fontWeight="" fontSize="lg">
              {name} {surname}
            </Box>
            <HStack>
                <Box as="span" fontSize={isMobile ? 'sm' : 'lg'}>{t("scoreLabel")}:</Box>
                {Array(5)
                  .fill('')
                  .map((_, i) => (
                    <StarIcon
                      key={i}
                      color={i < score ? 'yellow.500' : 'gray.300'}
                      boxSize={isMobile ? 4 : 5}
                    />
                  ))}
            </HStack>
            <Box color="gray.500">
              {description}
            </Box>
            {/* surname */}
            {/* <Text color="gray.500">@{surname}</Text> */}
          </VStack>
        </HStack>
      </Box>
    )
}

export default SingleReview