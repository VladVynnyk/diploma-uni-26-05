"use client"
import React, { useState, useEffect } from 'react';
import {
  Box, Image, Text, Tag, Button, HStack, VStack, SimpleGrid, useBreakpointValue, useMediaQuery, Drawer, DrawerBody, DrawerHeader, DrawerOverlay, DrawerContent, DrawerCloseButton, Spinner, Center, CSSReset
} from '@chakra-ui/react';
import {
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
} from '@chakra-ui/react'

import { StarIcon } from '@chakra-ui/icons';
import { TLoggedInUser, TUser } from "@/app/types/UserTypes";
import CurrentChat from '@/app/dashboard/Chats/CurrentChat';
import SingleReview from '@/app/dashboard/Reviews/SingleReview';

import usePrefixedTranslation from '../../hooks/usePrefixedTranslation'
import OrderForm from './OrderForm';


type userCardProps = {
  user: TUser
}

const UserCard = ({ user }: userCardProps) => {
  const { t } = usePrefixedTranslation('Components.ConsultantCard');

  console.log("USER: ", user)

  const [isExpanded, setIsExpanded] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isOrderOpen, setIsOrderOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);
  
  const toggleExpand = () => setIsExpanded(!isExpanded);
  const toggleChat = () => setIsChatOpen(!isChatOpen);
  const toggleOrder = () => setIsOrderOpen(!isOrderOpen);

  const cardWidth = useBreakpointValue({ base: '100%', md: '500px', lg: '600px' });
  const [isMobile] = useMediaQuery("(max-width: 480px)");

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000); // Simulate loading time
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    const storedUser = localStorage.getItem('currentUser');

    if (!storedUser) {
      return;
    }

    try {
      const parsedUser: TLoggedInUser = JSON.parse(storedUser);
      setCurrentUserId(parsedUser.id);
    } catch (error) {
      console.error("Failed to parse current user", error);
    }
  }, []);

  const isOwnConsultantCard = currentUserId === user.id;

  const chats = [
    { id: "1", name: 'Chat 1', photo: 'https://via.placeholder.com/150' },
    { id: "2", name: 'Chat 2', photo: 'https://via.placeholder.com/150' },
    { id: "3", name: 'Chat 3', photo: 'https://via.placeholder.com/150' }
  ];


  const messages = [
    { id: "1", text: 'Hello!', sender: 'user' },
    { id: "2", text: 'How are you?', sender: 'friend' },
    { id: "3", text: 'I am fine, thank you!', sender: 'user' }
  ];

  return (
    <>
      <CSSReset />
      {isLoading ? (
        <Center h="200px">
          <Spinner size="xl" />
        </Center>
      ) : (
        <Box
          borderWidth="1px"
          borderRadius="lg"
          overflow="hidden"
          marginBottom="4"
          p={4}
          w={cardWidth}
          maxW={cardWidth}
          transition="all 0.3s"
          display="flex"
          flexDirection="column"
          justifyContent="space-between"
        >
          <HStack alignItems="flex-start">
            <Image
              borderRadius="md"
              boxSize="100px"
              src={user.photo}
              alt={`${user.name} ${user.surname}`}
            />
            <VStack alignItems="flex-start" ml={3} flex="1">
              <Box fontWeight="bold" fontSize="2xl">
                {user.name} {user.surname}
              </Box>
              <HStack>
                <Text fontSize={isMobile ? 'sm' : 'lg'}>{t("scoreLabel")}:</Text>
                {Array(5)
                  .fill('')
                  .map((_, i) => (
                    <StarIcon
                      key={i}
                      color={i < user.averageScore ? 'yellow.500' : 'gray.300'}
                      boxSize={isMobile ? 4 : 5}
                    />
                  ))}
              </HStack>
              <HStack>
                <Text fontSize={isMobile ? 'sm' : 'lg'}>{t("priceLabel")}:</Text>
                <Text fontSize={isMobile ? 'sm' : 'lg'}>${user.pricePerHour}/{t("hourLabel")}</Text>
              </HStack>
            </VStack>
          </HStack>
          <Box mt={4}>
            <HStack wrap="wrap">
              {user.tags.map((tag, index) => (
                <Tag key={index} size={isMobile ? "md" : "lg"} variant="solid" colorScheme="blue" m={1}>
                  {tag.name}
                </Tag>
              ))}
            </HStack>
          </Box>
          <Box mt={4} fontSize="lg">
          {isExpanded 
            ? user.description || "No description available." 
            : `${(user.description || "No description available.").slice(0, 40)}...`}
            {isExpanded && (
              <Accordion allowToggle mt={4}>
                <AccordionItem>
                    <AccordionButton 
                    // bg="teal.300"           // Background color
                    // _hover={{ bg: "teal.200" }}  // Hover styles
                    // _expanded={{ bg: "teal.700", color: "white" }} // Styles when expanded
                    // borderRadius="md"       // Rounded corners
                    // px={4}                  // Padding (horizontal)
                    // py={2}                  // Padding (vertical)
                    >
                      <Box as="span" flex="1" textAlign="left">
                        {t("reviewsLabel")}
                      </Box>
                      <AccordionIcon />
                    </AccordionButton>
                  <Box as="span" flex="1" textAlign="left">
                    <AccordionPanel pb={4} 
                                    display={"flex"} 
                                    justifyContent={"center"} 
                                    alignItems={"center"} 
                                    flexDirection={"column"} 
                                    gap={2}>
                      {user.reviews.length > 0 ? (
                        user.reviews.map((review) => (
                          <SingleReview
                            key={review.id} // Ensure unique key
                            name={review.client.first_name}
                            surname={review.client.last_name}
                            description={review.description}
                            score={review.rating}
                            isMobile={isMobile}
                          />
                        ))
                      ) : (
                        <Text color="gray.500" textAlign="center">
                          {t("reviewsAreEmptyLabel")}
                        </Text>
                      )}
                    </AccordionPanel>
                  </Box>
                </AccordionItem>
              </Accordion>
            )}
          </Box>
          <SimpleGrid columns={isOwnConsultantCard ? 1 : 2} spacing={4} mt={4}>
          {/* <SimpleGrid columns={3} spacing={4} mt={4}> */}
            <Button onClick={toggleExpand} colorScheme="teal">
              {isExpanded ? t('collapseLabel') : t('detailsLabel')}
            </Button>
            {/* <Button colorScheme="blue" onClick={toggleChat}>{t("chatLabel")}</Button> */}
            {!isOwnConsultantCard && (
              <Button colorScheme="green" onClick={toggleOrder}>{t("buyLabel")}</Button>
            )}
          </SimpleGrid>
        </Box>
      )}

      <Drawer isOpen={isChatOpen} placement="right" onClose={toggleChat} size="md">
        <DrawerOverlay>
          <DrawerContent>
            <DrawerCloseButton />
            <DrawerHeader>{user.name} {user.surname}</DrawerHeader>
            <DrawerBody>
              <CurrentChat chat={chats.find(chat => chat.id === user.id) || chats[0]}
              messages={messages}/>
            </DrawerBody>
          </DrawerContent>
        </DrawerOverlay>
      </Drawer>

      <Drawer isOpen={isOrderOpen && !isOwnConsultantCard} placement="right" onClose={toggleOrder} size="md">
        <DrawerOverlay>
          <DrawerContent>
            <DrawerCloseButton />
            <DrawerHeader>{t("orderConsultationLabel")} {user.name} {user.surname}</DrawerHeader>
            <DrawerBody>
              {/* <Payment payment={payments.find(payment => payment.id === user.id) || payments[0]}></Payment> */}
              <OrderForm consultantId={user.id} price={user.pricePerHour}></OrderForm>
            </DrawerBody>
          </DrawerContent>
        </DrawerOverlay>
      </Drawer>
    </>
  );
};

export default UserCard;
