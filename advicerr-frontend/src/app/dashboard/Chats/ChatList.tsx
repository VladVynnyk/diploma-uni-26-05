import React from 'react'
import { 
    VStack, Button
  } from '@chakra-ui/react';
import { TChat } from '@/app/types/ChatTypes';

type TOnSelect = (arg: number | string | null) => void;


type ChatListProps = {
  chats: Array<TChat>,
  // onSelect: TOnSelect
  onSelect: React.Dispatch<React.SetStateAction<string | null>>
}

const ChatList = (props: ChatListProps) => {
  return(
    <VStack spacing={4} align="stretch">
      {props.chats.map(chat => (
        <Button key={chat.id} onClick={() => props.onSelect(chat.id)}>
          {chat.name}
        </Button>
      ))}
    </VStack>
    )
};

export default ChatList