"use client"
import React from "react";
import MainContainer from "./components/MainContainer/MainContainer";
import FilterButton from "./components/FilterMenu/FilterButton";
import UserCard from "./components/ConsultationCard/ConsultantCardV3";
import Pagination from "./components/Pagination/Pagination";
import StatusState from "./components/StatusState/StatusState";
import { useGetPaginatedUsersQuery, useGetPaginatedUsersWTagsQuery } from "./store/apis/usersApi";
import { skipToken } from "@reduxjs/toolkit/query";
import { User } from "./types/UserTypes";

import usePrefixedTranslation from "./hooks/usePrefixedTranslation";


export default function Home() {
  const { t } = usePrefixedTranslation("Pages.HomePage")

  const [page, setPage] = React.useState(1);
  const [users, setUsers] = React.useState<Array<User>>([]);
  const [selectedTag, setSelectedTag] = React.useState<string | null>(null);
  const pageSize = 10;

  // Fetch all users initially
  const {
    data: paginatedData,
    isLoading: isPaginatedLoading,
    error: paginatedError,
  } = useGetPaginatedUsersQuery({ page, pageSize }, { skip: !!selectedTag }); // Skip if a tag is selected

  // Fetch users filtered by tag (only when a tag is selected)
  const {
    data: filteredData,
    isLoading: isFilteredLoading,
    error: filteredError,
  } = useGetPaginatedUsersWTagsQuery(
    selectedTag ? { tagName: selectedTag, page, pageSize } : skipToken, // Skip if no tag is selected
    { skip: !selectedTag } // Skip this query when no tag is selected
  );
  
  // Debugging logs
  console.log("PAGINATED DATA: ", paginatedData);
  console.log("FILTERED DATA: ", filteredData);
  console.log("SELECTED TAG: ", selectedTag);
  

  React.useEffect(() => {
    console.log("RAW FILTERED DATA:", filteredData?.users);
    console.log("RAW PAGINATED DATA:", paginatedData?.users);
  
    if (selectedTag) {
      if (filteredData && filteredData.users?.length > 0) {
        setUsers(filteredData.users);
      } else {
        setUsers([]); // Ensure UI shows "No users found"
      }
    } else {
      if (paginatedData && paginatedData.users?.length > 0) {
        setUsers(paginatedData.users);
      } else {
        setUsers([]);
      }
    }
  }, [paginatedData, filteredData, selectedTag]);
  
  // Use another `useEffect` to track changes in `users`
  React.useEffect(() => {
    console.log("UPDATED USERS: ", users);
  }, [users]);
  
  const isCurrentLoading = selectedTag ? isFilteredLoading : isPaginatedLoading;
  const currentError = selectedTag ? filteredError : paginatedError;
  const shouldShowPagination = !selectedTag && !!paginatedData?.total_count && users.length > 0;

  return (
    <MainContainer>
      <div className="flex flex-col items-center justify-between">
        {/* <h1 className="text-4xl">Консультації</h1> */}
        <h1 className="text-4xl">{t("headerTitle")}</h1>

        {/* Filter Button for Selecting Tags */}
        <FilterButton
          label={t("filterButtonLabel")}
          action="chooseCategory"
          onSelectTag={(tag) => {
            setSelectedTag(tag);
            setPage(1);
          }}
          onCancel={() => {
            setSelectedTag(null);
            setPage(1);
          }}
        />

        {isCurrentLoading ? (
          <StatusState message={t("loadingLabel")} variant="loading" />
        ) : currentError ? (
          <StatusState message={t("errorLoadingUsersLabel")} variant="error" />
        ) : users.length > 0 ? (
          users.map((user) => (
            <UserCard
              key={user.id}
              user={{
                id: user.id,
                photo: user.photo,
                name: user.first_name,
                surname: user.last_name,
                averageScore: user.rating,
                pricePerHour: user.price,
                tags: user.tags,
                description: user.description,
                reviews: user.reviews_as_consultant,
              }}
            />
          ))
        ) : (
          <StatusState message={t("errorUsersNotFoundLabel")} variant="empty" />
        )}

        {shouldShowPagination && (
          <Pagination
            currentPage={page}
            totalPages={Math.ceil(paginatedData.total_count / pageSize)}
            onPageChange={(newPage) => setPage(newPage)}
          />
        )}
      </div>
    </MainContainer>
  );
}
