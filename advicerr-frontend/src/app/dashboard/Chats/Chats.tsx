import React, { useState } from 'react';
import {
  Box, HStack, Heading
} from '@chakra-ui/react';
import ChatList from './ChatList';
import CurrentChat from './CurrentChat';
import { TChat } from '@/app/types/ChatTypes';
import usePrefixedTranslation from '@/app/hooks/usePrefixedTranslation';

type chatsProps = {
    isMobile: boolean
  } 

const Chats: React.FC<chatsProps> = ({ isMobile }: chatsProps) => {
    const { t } = usePrefixedTranslation('Pages.DashboardPage.chats');
    const [selectedChat, setSelectedChat] = useState<string | null>(null);
    const chats: Array<TChat> = [
      { id: "1", name: 'Chat 1' },
      { id: "2", name: 'Chat 2' },
      { id: "3", name: 'Chat 3' }
    ];
  
    const messages = [
      { id: "1", text: 'Hello!', sender: 'user' },
      { id: "2", text: 'How are you?', sender: 'friend' },
      { id: "3", text: 'I am fine, thank you!', sender: 'user' }
    ];
    return (
      <Box h="full">
        <Heading as="h2" size="xl" mb={4}>
          {t('chatsLabel')}
        </Heading>
        {isMobile ? (
          selectedChat ? (
            <CurrentChat
              chat={chats.find(chat => chat.id === selectedChat) || null} // If chat is not found, instead of undefined will return null
              messages={messages}
              goBack={() => setSelectedChat(null)}
              isMobile={isMobile}
            />
          ) : (
            <ChatList chats={chats} onSelect={setSelectedChat} />
          )
        ) : (
          <HStack align="stretch" h="80vh">
            <Box w="30%" borderRight="1px" borderColor="gray.200" p={4} overflowY="auto">
              <ChatList chats={chats} onSelect={setSelectedChat} />
            </Box>
            <Box w="70%" p={4} display="flex" flexDirection="column" h="full">
              <CurrentChat
                chat={chats.find(chat => chat.id === selectedChat) || chats[0]}
                messages={messages}
                isMobile={isMobile}
                goBack={() => setSelectedChat(null)}
              />
            </Box>
          </HStack>
        )}
      </Box>
    );
  };

export default Chats