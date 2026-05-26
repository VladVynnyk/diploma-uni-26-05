import React from 'react';
import { Flex,
  Box, VStack, HStack, Button, Heading, Input
} from '@chakra-ui/react';
import {TChat, TMessage} from "@/app/types/ChatTypes";

import usePrefixedTranslation from '../../hooks/usePrefixedTranslation'

type TGoBack = () => void;

type CurrentChatProps = {
  chat: TChat | null,
  // Also, here can be optional value: 
  // chat?: TChat;
  messages: Array<TMessage>,
  goBack?: TGoBack,
  isMobile?: boolean
}

const CurrentChat = ({ chat, messages, goBack, isMobile }: CurrentChatProps) => {
  const { t } = usePrefixedTranslation('Components.Chats');
  
  if (!chat) {
    return <div>Unexpected error</div>;
  }
  
  return (
    <Box h="90%" display="flex" flexDirection="column">
      {/* {goBack && (
        <Button
          leftIcon={<ArrowBackIcon />}
          onClick={goBack}
          mb={4}
          colorScheme="teal"
        >
          Go back to chats
        </Button>
      )} */}
      <Heading as="h3" size="lg" mb={4}>
        {chat.name}
      </Heading>
      <VStack spacing={4} align="stretch" flex="1" overflowY="auto">
        {messages.map((message, index) => (
          <Flex
            key={index}
            p={4}
            bg={message.sender === 'user' ? 'teal.100' : 'gray.100'}
            alignSelf={message.sender === 'user' ? 'flex-end' : 'flex-start'}
            borderRadius="md"
            maxWidth="80%"
          >
            {message.text}
          </Flex>
        ))}
      </VStack>
      <Box p={4} bg="white" boxShadow="lg">
        <HStack spacing={4}>
          <Input placeholder={t("writeMessageLabel")}/>
          <Button colorScheme="teal">{t("sendButtonLabel")}</Button>
        </HStack>
      </Box>
    </Box>
  )
};

export default CurrentChat