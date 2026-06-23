/**
 * dashboard2026/src/pages/memecoin/TokenProfilingPage.tsx
 * Memecoin Token Profiling Page
 * 
 * Community metadata management, social sentiment tracking, and developer reputation
 * Inspired by DexScreener's token profiles and community takeover tracking
 */

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { getMemecoinAPI, type Blockchain, type TokenProfile, formatTokenAddress } from '@/api/memecoin';

export function TokenProfilingPage() {
  const [selectedChain, setSelectedChain] = useState<Blockchain>('solana');
  const [tokenAddress, setTokenAddress] = useState('');

  return (
    <div className="flex h-full flex-col bg-slate-900 text-slate-100">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Token Profiling</h1>
            <p className="text-slate-400 text-sm mt-1">
              Community metadata and token reputation management
            </p>
          </div>
          <div className="flex items-center gap-4">
            <select
              value={selectedChain}
              onChange={(e) => setSelectedChain(e.target.value as Blockchain)}
              className="bg-slate-700 border border-slate-600 rounded px-3 py-2 text-sm"
            >
              <option value="solana">Solana</option>
              <option value="ethereum">Ethereum</option>
              <option value="bsc">BSC</option>
              <option value="base">Base</option>
            </select>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Create Token Profile */}
          <CreateProfile
            tokenAddress={tokenAddress}
            setTokenAddress={setTokenAddress}
            selectedChain={selectedChain}
          />

          {/* Recent Profiles */}
          <RecentProfiles selectedChain={selectedChain} />
        </div>
      </div>
    </div>
  );
}

function CreateProfile({ tokenAddress, setTokenAddress, selectedChain }: { tokenAddress: string; setTokenAddress: (val: string) => void; selectedChain: Blockchain }) {
  const [profile, setProfile] = useState({
    name: '',
    description: '',
    category: '',
    tags: '',
    twitter: '',
    telegram: '',
    website: '',
  });

  const { mutate: createProfile, isPending } = useMutation({
    mutationFn: async () => {
      const profileData: Partial<TokenProfile> = {
        address: tokenAddress,
        chain: selectedChain,
        description: profile.description || undefined,
        metadata: {
          category: profile.category || undefined,
          tags: profile.tags ? profile.tags.split(',').map(t => t.trim()) : undefined,
          social_links: {
            twitter: profile.twitter || undefined,
            telegram: profile.telegram || undefined,
            website: profile.website || undefined,
          },
        },
      };
      return getMemecoinAPI().createTokenProfile(tokenAddress, selectedChain, profileData);
    },
    onSuccess: (data) => {
      console.log('Profile created:', data);
      setProfile({
        name: '',
        description: '',
        category: '',
        tags: '',
        twitter: '',
        telegram: '',
        website: '',
      });
      setTokenAddress('');
    },
  });

  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h2 className="text-xl font-bold text-white mb-4">📝 Create Token Profile</h2>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Token Address
          </label>
          <input
            type="text"
            value={tokenAddress}
            onChange={(e) => setTokenAddress(e.target.value)}
            placeholder="Enter token contract address..."
            className="w-full bg-slate-700 border border-slate-600 rounded px-4 py-2 text-sm placeholder-slate-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Token Name
          </label>
          <input
            type="text"
            value={profile.name}
            onChange={(e) => setProfile({ ...profile, name: e.target.value })}
            placeholder="Token name..."
            className="w-full bg-slate-700 border border-slate-600 rounded px-4 py-2 text-sm"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Description
          </label>
          <textarea
            value={profile.description}
            onChange={(e) => setProfile({ ...profile, description: e.target.value })}
            placeholder="Token description..."
            rows={3}
            className="w-full bg-slate-700 border border-slate-600 rounded px-4 py-2 text-sm"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Category
          </label>
          <select
            value={profile.category}
            onChange={(e) => setProfile({ ...profile, category: e.target.value })}
            className="w-full bg-slate-700 border border-slate-600 rounded px-4 py-2 text-sm"
          >
            <option value="">Select category...</option>
            <option value="ai">AI</option>
            <option value="agents">Agents</option>
            <option value="gaming">Gaming</option>
            <option value="meme">Meme</option>
            <option value="defi">DeFi</option>
            <option value="utility">Utility</option>
            <option value="charity">Charity</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Tags (comma-separated)
          </label>
          <input
            type="text"
            value={profile.tags}
            onChange={(e) => setProfile({ ...profile, tags: e.target.value })}
            placeholder="e.g. AI, defi, gaming"
            className="w-full bg-slate-700 border border-slate-600 rounded px-4 py-2 text-sm"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Social Links
          </label>
          <div className="space-y-3">
            <input
              type="text"
              value={profile.twitter}
              onChange={(e) => setProfile({ ...profile, twitter: e.target.value })}
              placeholder="Twitter URL..."
              className="w-full bg-slate-700 border border-slate-600 rounded px-4 py-2 text-sm"
            />
            <input
              type="text"
              value={profile.telegram}
              onChange={(e) => setProfile({ ...profile, telegram: e.target.value })}
              placeholder="Telegram URL..."
              className="w-full bg-slate-700 border border-slate-600 rounded px-4 py-2 text-sm"
            />
            <input
              type="text"
              value={profile.website}
              onChange={(e) => setProfile({ ...profile, website: e.target.value })}
              placeholder="Website URL..."
              className="w-full bg-slate-700 border border-slate-600 rounded px-4 py-2 text-sm"
            />
          </div>
        </div>

        <button
          onClick={() => createProfile()}
          disabled={!tokenAddress || isPending}
          className="w-full py-3 bg-blue-500 hover:bg-blue-600 disabled:bg-slate-600 disabled:cursor-not-allowed rounded font-medium text-white transition-colors"
        >
          {isPending ? 'Creating...' : 'Create Profile'}
        </button>
      </div>
    </div>
  );
}

function RecentProfiles({ selectedChain }: { selectedChain: Blockchain }) {
  const { data: profiles, isLoading } = useQuery({
    queryKey: ['memecoin', 'profiles', 'latest', selectedChain],
    queryFn: () => getMemecoinAPI().getLatestProfiles(selectedChain, 20),
    refetchInterval: 15000,
  });

  if (isLoading) {
    return (
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 className="text-xl font-bold text-white mb-4">📋 Recent Profiles</h2>
        <div className="text-center text-slate-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
      <h2 className="text-xl font-bold text-white mb-4">📋 Recent Profiles</h2>

      <div className="space-y-3">
        {profiles?.slice(0, 10).map((profile, index) => (
          <ProfileCard key={index} profile={profile} />
        ))}
      </div>
    </div>
  );
}

function ProfileCard({ profile }: { profile: TokenProfile }) {
  return (
    <div className="p-4 bg-slate-700/50 rounded-lg border border-slate-600 hover:border-slate-500 transition-colors">
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
          {profile.symbol?.slice(0, 2) || profile.address.slice(0, 2)}
        </div>
        <div className="flex-1">
          <div className="font-medium text-white mb-1">{profile.name}</div>
          <div className="font-mono text-xs text-slate-400 mb-2">{formatTokenAddress(profile.address)}</div>
          {profile.description && (
            <div className="text-xs text-slate-400 line-clamp-2">{profile.description}</div>
          )}
          <div className="flex flex-wrap gap-2 mt-2">
            {profile.metadata.category && (
              <span className="px-2 py-0.5 bg-purple-500/20 text-purple-400 rounded text-xs">
                {profile.metadata.category}
              </span>
            )}
            {profile.metadata.tags?.map((tag, idx) => (
              <span key={idx} className="px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded text-xs">
                {tag}
              </span>
            ))}
          </div>
          {profile.metadata.social_links && (
            <div className="flex gap-3 mt-2">
              {profile.metadata.social_links.twitter && (
                <a href={profile.metadata.social_links.twitter} target="_blank" className="text-xs text-blue-400 hover:text-blue-300">
                  Twitter
                </a>
              )}
              {profile.metadata.social_links.telegram && (
                <a href={profile.metadata.social_links.telegram} target="_blank" className="text-xs text-blue-400 hover:text-blue-300">
                  Telegram
                </a>
              )}
              {profile.metadata.social_links.website && (
                <a href={profile.metadata.social_links.website} target="_blank" className="text-xs text-blue-400 hover:text-blue-300">
                  Website
                </a>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}