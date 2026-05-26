"use client"
import React from 'react'
import { useGetTagsQuery } from '@/app/store/apis/tagsApi'
import { Menu, MenuButton, MenuItem, Button, MenuList, MenuGroup } from '@chakra-ui/react'
import { ChevronDownIcon } from '@chakra-ui/icons'

import usePrefixedTranslation from '@/app/hooks/usePrefixedTranslation';

type Props = {
  label: string;
  action: "chooseCategory" | "sort";
  onSelectTag: (tag: string) => void;
  onCancel: () => void;
}

const FilterButton = ({label, action, onSelectTag, onCancel}: Props) => {
  const {
    data: options,
    isLoading: isPaginatedLoading,
    error: paginatedError,
  } = useGetTagsQuery();

  const { t } = usePrefixedTranslation('Components.FilterButton')
  const loadFailedLabel = "Не вийшло завантажити фільтри";
  const emptyLabel = "Фільтри недоступні";

  return (
    <div>
      <Menu>
          <MenuButton as={Button} rightIcon={<ChevronDownIcon/>} colorScheme='teal' m={2}>
              {label}
          </MenuButton>
          <MenuList>
              {action == "sort" ? <MenuGroup title={t("onPriceFilterLabel")}/> : ''}
              {paginatedError && (
                <MenuItem isDisabled>
                  {loadFailedLabel}
                </MenuItem>
              )}
              {!paginatedError && !isPaginatedLoading && !options?.length && (
                <MenuItem isDisabled>
                  {emptyLabel}
                </MenuItem>
              )}
              {options?.map((opt)=>
                <MenuItem key={opt.id} onClick={() => onSelectTag(opt.name)}>
                {opt.name}
                </MenuItem>
              )}
              <MenuItem key={"Cancel"} onClick={() => onCancel()}>
              Скасувати
              </MenuItem>
          </MenuList>
      </Menu>
    </div>
  )
}

export default FilterButton
