"""
Vector GraphQL MCP Server
--------------------------------
This server provides tools to fetch Vector leaderboard data and profile information
using GraphQL queries.
"""

from typing import Dict, List, Optional, Any, Union
import httpx
from mcp.server.fastmcp import FastMCP, Context

# Create server
mcp = FastMCP("Vector GraphQL")

# API endpoint and headers
API_URL = "https://mainnet-api.vector.fun/graphql"
HEADERS = {
    "Host": "mainnet-api.vector.fun",
    "content-type": "application/json",
    "X-App-Version": "1.11.0",
    "X-App-Build-Number": "331",
    "accept": "*/*",
    "x-app-name": "Vector",
    "Accept-Language": "en-US;q=1",
    "user-agent": "Vector/331 CFNetwork/1568.200.51 Darwin/24.1.0",
    "pragma": "no-cache",
    "cache-control": "no-cache"
}

# GraphQL queries
LEADERBOARD_QUERY = """
query leaderboardScreenQuery(
  $groupId: String
  $leaderboardType: LeaderboardType!
  $periodsAgo: Int
  $first: Int
  $after: String
) {
  ...leaderboardFragment_31k55b
}

fragment InlineProfileFragment on Profile {
  id
  ...ProfilePicFragment
  ...ProfileUsernameFragment
}

fragment LeaderboardEntryFragment on LeaderboardEntry {
  profileId
  broadcastCount
  rank
  value
  percentileV2
  profile {
    id
    username
    profileImageUrl
    twitterUsername
    isVerified
    followerCount
    followerCountX
    ...InlineProfileFragment
    ...ProfilePicFragment
  }
}

fragment ProfileBadgesFragment on Profile {
  username
  twitterUsername
  isVerified
}

fragment ProfilePicFragment on Profile {
  id
  username
  moderationState
  profileImageUrl
  ...ProfileBadgesFragment
}

fragment ProfileUsernameFragment on Profile {
  username
  moderationState
  ...ProfileBadgesFragment
}

fragment leaderboardFragment_31k55b on Query {
  leaderboardWeekly(leaderboardType: $leaderboardType, groupId: $groupId, periodsAgo: $periodsAgo, first: $first, after: $after) {
    edges {
      node {
        profileId
        ...LeaderboardEntryFragment
        __typename
      }
      cursor
    }
    resetsAt
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}
"""

# Profile query for detailed trader info
PROFILE_QUERY = """
query UsernameProfileQuery(
  $username: String!
  $cursor: String
  $count: Int
) {
  profile(username: $username, refcode: $username) {
    id
    username
    moderationState
    twitterUsername
    followerCountX
    followerCount
    weeklyLeaderboardStanding(leaderboardType: PNL_WIN) {
      rank
      value
    }
    profileLeaderboardValues {
      daily {
        pnl
        volume
        maxTradeSize
      }
      weekly {
        pnl
        volume
        maxTradeSize
      }
    }
  }
  userHoldings(id: $username, after: $cursor, first: $count) {
    edges {
      cursor
      node {
        portfolioPercentage
        token {
          id
          address
          chain
          name
          symbol
          image
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
  userBroadcastsV2(id: $username, after: $cursor, first: $count) {
    edges {
      cursor
      node {
        broadcast {
          id
          message
          createdAt
          buyTokenId
          buyTokenAmount
          buyPositionSize
          buyTokenPrice: buyTokenPriceV2
          sellTokenId
          sellTokenAmount
          sellPositionSize
          sellTokenPrice: sellTokenPriceV2
          broadcastCandleChart {
            cycleStats {
              pnl
              totalBought
              totalHeld
              totalSold
            }
          }
        }
        buyToken {
          id
          chain
          name
          symbol
          price
          image
          address
        }
        sellToken {
          id
          chain
          name
          symbol
          price
          image
          address
        }
      }
    }
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}
"""

# Token list query
TOKENS_LIST_QUERY = """
query TokensListRefetchQuery(
    $count: Int = 25
    $cursor: String
    $filterBy: String
    $query: String
    $sortBy: String
) {
    searchTokens(query: $query, sortBy: $sortBy, filterBy: $filterBy, after: $cursor, first: $count) {
        edges {
            node {
                id
                address
                chain
                symbol
                price
                supply
                volume5min
                volume1h
                volume6h
                volume24h
                broadcastCount5min
                broadcastCount1h
                broadcastCount6h
                broadcastCount24h
                top10HolderPercentV2
                firstIndexedTimestamp
                insiderHoldingPercent
                devHoldingPercent
            }
        }
    }
}
"""

# Token broadcasts query
TOKEN_BROADCASTS_QUERY = """
query TokenBroadcastsQuery(
    $id: ID!
    $after: String
    $first: Int = 100
    $sortBy: TokenBroadcastSortBy
    $sortDirection: TokenBroadcastSortDirection
) {
    tokenBroadcasts(
        id: $id
        after: $after
        first: $first
        sortBy: $sortBy
        sortDirection: $sortDirection
    ) {
        edges {
            node {
                broadcast {
                    message
                }
            }
        }
    }
}
"""

@mcp.tool(name="fetch_leaderboard")
async def fetch_leaderboard(
    leaderboard_type: str = "PNL_WIN",
    ctx: Context = None
) -> str:
    """Fetch Vector leaderboard data
    
    Args:
        leaderboard_type: Type of leaderboard (e.g., 'PNL_WIN', 'TRADE_VOLUME')
        
    Returns:
        JSON string with leaderboard data
    """
    if ctx:
        ctx.info(f"Fetching {leaderboard_type} leaderboard data...")
    
    # Hardcoded variables as requested
    variables = {
        "after": None,
        "first": 100,
        "groupId": None,
        "leaderboardType": leaderboard_type,
        "periodsAgo": None
    }
    
    payload = {
        "query": LEADERBOARD_QUERY,
        "variables": variables
    }
    
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(
                API_URL, 
                json=payload, 
                headers=HEADERS
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            error_message = f"Error fetching leaderboard data: {str(e)}"
            if ctx:
                ctx.error(error_message)
            return error_message

@mcp.tool(name="fetch_profile")
async def fetch_profile(
    username: str,
    ctx: Context = None
) -> str:
    """Fetch detailed profile data for a Vector trader
    
    Args:
        username: Vector username to fetch
        
    Returns:
        JSON string with profile data
    """
    if ctx:
        ctx.info(f"Fetching profile data for {username}...")
    
    # Hardcoded variables as requested
    variables = {
        "username": username,
        "cursor": None,
        "count": 10
    }
    
    payload = {
        "query": PROFILE_QUERY,
        "variables": variables
    }
    
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(
                API_URL, 
                json=payload, 
                headers=HEADERS
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            error_message = f"Error fetching profile data: {str(e)}"
            if ctx:
                ctx.error(error_message)
            return error_message

@mcp.tool(name="fetch_token_data")
async def fetch_token_data(
    ctx: Context = None
) -> str:
    """Fetch trending Solana tokens from Vector
    
    Returns:
        JSON string with token data
    """
    if ctx:
        ctx.info("Fetching trending Solana tokens...")
    
    # Hardcoded variables as requested
    variables = {
        "count": 50,
        "cursor": None,
        "filterBy": "(broadcastCount5minV2:>0) && (chain:SOLANA)",
        "query": None,
        "sortBy": "trendingScore5min:desc"
    }
    
    payload = {
        "query": TOKENS_LIST_QUERY,
        "variables": variables
    }
    
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(
                API_URL, 
                json=payload, 
                headers=HEADERS
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            error_message = f"Error fetching token data: {str(e)}"
            if ctx:
                ctx.error(error_message)
            return error_message

@mcp.tool(name="fetch_token_broadcasts")
async def fetch_token_broadcasts(
    token_id: str,
    ctx: Context = None
) -> str:
    """Fetch broadcasts for a specific token
    
    Args:
        token_id: Vector token ID
        
    Returns:
        JSON string with token broadcasts
    """
    if ctx:
        ctx.info(f"Fetching broadcasts for token {token_id}...")
    
    # Hardcoded variables as requested
    variables = {
        "id": token_id,
        "after": None,
        "first": 100,
        "sortBy": "Time",
        "sortDirection": "Desc"
    }
    
    payload = {
        "query": TOKEN_BROADCASTS_QUERY,
        "variables": variables
    }
    
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(
                API_URL, 
                json=payload, 
                headers=HEADERS
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            error_message = f"Error fetching token broadcasts: {str(e)}"
            if ctx:
                ctx.error(error_message)
            return error_message 