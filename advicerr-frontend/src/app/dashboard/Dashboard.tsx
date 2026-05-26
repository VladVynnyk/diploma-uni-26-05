"use client"
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useToast } from '@chakra-ui/react';
import {
  Box, VStack, HStack, Button, Drawer, DrawerBody, DrawerFooter, DrawerHeader, DrawerOverlay, DrawerContent, DrawerCloseButton, useDisclosure, IconButton, useBreakpointValue
} from '@chakra-ui/react';
import { HamburgerIcon } from '@chakra-ui/icons';
import MainContainer from '../components/MainContainer/MainContainer';
import StatusState from '../components/StatusState/StatusState';
import PersonalInformation from './PersonalInformation/PersonalInformation';
import Reviews from './Reviews/Reviews';
import Orders from './Orders/Orders';
import AdminUsers from './admin/AdminUsers';
import AdminOrders from './admin/AdminOrders';
import AdminReviews from './admin/AdminReviews';
import AdminStats from './admin/AdminStats';
import AdminTags from './admin/AdminTags';

import usePrefixedTranslation from '../hooks/usePrefixedTranslation'
import { useGetMeQuery, useRefreshTokenMutation } from '../store/apis/usersApi';

import Cookies from 'js-cookie';

const Dashboard = () => {
  const { t } = usePrefixedTranslation('Pages.DashboardPage');

  const token = Cookies.get("access_token") || "";

  const { data, error, isLoading } = useGetMeQuery(token);
  const [refreshToken] = useRefreshTokenMutation();

  const [selectedMenu, setSelectedMenu] = useState("Personal Information");
  const { isOpen, onOpen, onClose } = useDisclosure();
  const btnRef = React.useRef<HTMLButtonElement | null>(null);
  const sidebarWidth = useBreakpointValue({ base: "100%", md: "250px" });
  const isMobile: boolean = useBreakpointValue({ base: true, md: false }) ?? false;

  const toast = useToast();
  const router = useRouter();

  React.useEffect(() => {
    const refreshAuthToken = async () => {
      try {
        const refreshTokenFromCookies = Cookies.get("refresh_token");
        if (!refreshTokenFromCookies) {
          throw new Error("No refresh token found");
        }

        const newTokens = await refreshToken({ refresh_token: refreshTokenFromCookies }).unwrap();

        Cookies.set("access_token", newTokens.access_token);
        Cookies.set("refresh_token", newTokens.refresh_token);
      } catch (refreshError) {
        console.error("Token refresh failed:", refreshError);
        toast({
          title: t("personalInfo.errorToastLabel"),
          description: t("personalInfo.sessionEndedError"),
          status: "error",
          duration: 3000,
          isClosable: true,
        });

        Cookies.remove("access_token");
        Cookies.remove("refresh_token");
        setTimeout(() => {
          router.push("/login");
        }, 5000);
      }
    };

    if (error) {
      refreshAuthToken();
    }
  }, [error, refreshToken, toast, router, t]);

  if (data) {
    const { password, ...userWithoutPassword } = data
    localStorage.setItem("currentUser", JSON.stringify(userWithoutPassword))
  }

  const menuItems = [
    { key: 'Personal Information', label: t("personalInfo.personalInformationLabel") },
    { key: 'Reviews', label: t("reviews.reviewsLabel") },
    { key: 'Orders', label: t("orders.ordersLabel") },
    ...(data?.is_admin ? [
      { key: 'Admin Users', label: 'Усі користувачі' },
      { key: 'Admin Orders', label: 'Усі замовлення' },
      { key: 'Admin Reviews', label: 'Усі відгуки' },
      { key: 'Admin Tags', label: 'Усі теги' },
      { key: 'Admin Stats', label: 'Статистика' },
    ] : [])
  ];

  const renderContent = () => {
    if (!data) {
      return null;
    }

    switch (selectedMenu) {
      case 'Personal Information':
        return <PersonalInformation props={data} />;
      case 'Reviews':
        return <Reviews id={data.id} reviews={data.reviews_as_consultant}/>;
      case 'Orders':
        return <Orders currentUser={data} />;
      case 'Admin Users':
        return <AdminUsers token={token} currentUserId={data.id} />;
      case 'Admin Orders':
        return <AdminOrders token={token} />;
      case 'Admin Reviews':
        return <AdminReviews token={token} />;
      case 'Admin Tags':
        return <AdminTags token={token} />;
      case 'Admin Stats':
        return <AdminStats token={token} />;
      default:
        return <PersonalInformation props={data} />;
    }
  };

  return (
    <MainContainer>
      {isLoading ? (
        <StatusState message={t("loadingLabel")} variant="loading" />
      ) : error || !data ? (
        <StatusState message={t("personalInfo.sessionEndedError")} variant="error" />
      ) : (
        <div>
          {isMobile && (
            <IconButton
              icon={<HamburgerIcon />}
              onClick={onOpen}
              ref={btnRef}
              colorScheme="teal"
              aria-label="Open Menu"
              position="fixed"
              bottom={4}
              right={4}
              zIndex={1}
            />
          )}
          <HStack align="stretch" h="100vh">
            {!isMobile && (
              <VStack
                w={sidebarWidth}
                p={4}
                spacing={4}
                align="stretch"
              >
                {menuItems.map((item) => (
                  <Button
                    key={item.key}
                    variant={selectedMenu === item.key ? 'solid' : 'ghost'}
                    colorScheme="teal"
                    onClick={() => setSelectedMenu(item.key)}
                    w="full"
                  >
                    {item.label}
                  </Button>
                ))}
              </VStack>
            )}
            <Box p={8} flex="1" overflowY="auto">
              {renderContent()}
            </Box>
          </HStack>

          <Drawer
            isOpen={isOpen}
            placement="left"
            onClose={onClose}
            finalFocusRef={btnRef}
          >
            <DrawerOverlay>
              <DrawerContent>
                <DrawerCloseButton />
                <DrawerHeader>{t("menuLabel")}</DrawerHeader>
                <DrawerBody>
                  <VStack spacing={4} align="stretch">
                    {menuItems.map((item) => (
                      <Button
                        key={item.key}
                        variant={selectedMenu === item.key ? 'solid' : 'ghost'}
                        colorScheme="teal"
                        onClick={() => {
                          setSelectedMenu(item.key);
                          onClose();
                        }}
                        w="full"
                      >
                        {item.label}
                      </Button>
                    ))}
                  </VStack>
                </DrawerBody>
                <DrawerFooter>
                  <Button variant="outline" mr={3} onClick={onClose}>
                    {t("closeMobileMenuLabel")}
                  </Button>
                </DrawerFooter>
              </DrawerContent>
            </DrawerOverlay>
          </Drawer>
        </div>
      )}
    </MainContainer>
  );
};

export default Dashboard;
