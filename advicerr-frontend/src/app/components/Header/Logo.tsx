import React from 'react'
import { Box, Text, Stack } from "@chakra-ui/react";

type Props = {}

const Logo = (props: Props) => {
    return (
        <Stack direction="row" align="center" spacing={1}>
          <Text
            fontSize={{ base: "2xl", md: "3xl" }}
            fontWeight="bold"
            bgGradient="linear(to-r, teal.400, blue.500)"
            bgClip="text"
          >
            Advicerr
          </Text>
          {/* <Text
            fontSize={{ base: "2xl", md: "3xl" }}
            fontWeight="extrabold"
            color="teal.500"
          >
            Advicerr
          </Text> */}
        </Stack>
    );
}

export default Logo