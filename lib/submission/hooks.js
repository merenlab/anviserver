import { fetcher } from '@/lib/fetch';
import useSWR from 'swr';
import useSWRInfinite from 'swr/infinite';

export function useSubmitPages() {
  return useSWR('/api/submissions', fetcher);
}

export function useSubmitProfile({ creatorId } = {}) {
  const { data, error, size, ...props } = useSWRInfinite(
    (index, previousPageData) => {
      // reached the end
      if (previousPageData && previousPageData.submissions.length === 0)
        return null;

      const searchParams = new URLSearchParams();

      if (creatorId) searchParams.set('by', creatorId);

      if (index !== 0) {
        // using oldest posts createdAt date as cursor
        // We want to fetch posts which has a date that is
        // before (hence the .getTime()) the last post's createdAt
        const before = new Date(
          new Date(
            previousPageData.submissions[
              previousPageData.submissions.length - 1
            ].createdAt
          ).getTime()
        );

        searchParams.set('before', before.toJSON());
      }

      return `/api/submissions?${searchParams.toString()}`;
    },
    fetcher,
    {
      refreshInterval: 10000,
      revalidateAll: false,
    }
  );

  const isLoadingInitialData = !data && !error;
  const isLoadingMore =
    isLoadingInitialData ||
    (size > 0 && data && typeof data[size - 1] === 'undefined');
  const isEmpty = data?.[0]?.length === 0;
  const isReachingEnd =
    isEmpty || (data && data[data.length - 1]?.submissions?.length < 5);

  return {
    data,
    error,
    size,
    isLoadingMore,
    isReachingEnd,
    ...props,
  };
}
