'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Lightbulb, Sparkles, TrendingUp, Hash } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { contentAPI } from '@/services/api'

interface ContentIdea {
    id: string
    title: string
    description: string
    engagement_score: number
    hashtags: string[]
    platform_optimized?: string
}

export default function ContentIdeaGenerator() {
    const [formData, setFormData] = useState({
        topic: '',
        niche: '',
        audience: '',
        count: 5,
        platform: ''
    })
    const [isLoading, setIsLoading] = useState(false)
    const [ideas, setIdeas] = useState<ContentIdea[]>([])
    const { toast } = useToast()

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsLoading(true)

        try {
            const response = await contentAPI.generateIdeas(formData)
            setIdeas(response.data)
            toast({
                title: "Ideas Generated! 🎉",
                description: `Generated ${response.data.length} content ideas for you.`,
            })
        } catch (error: any) {
            toast({
                title: "Generation Failed",
                description: error.response?.data?.detail || "Failed to generate ideas. Please try again.",
                variant: "destructive"
            })
        } finally {
            setIsLoading(false)
        }
    }

    const getEngagementColor = (score: number) => {
        if (score >= 80) return "bg-green-500"
        if (score >= 60) return "bg-yellow-500"
        return "bg-red-500"
    }

    const platforms = [
        { value: "youtube", label: "YouTube" },
        { value: "instagram", label: "Instagram" },
        { value: "tiktok", label: "TikTok" },
        { value: "linkedin", label: "LinkedIn" },
        { value: "twitter", label: "Twitter" }
    ]

    const niches = [
        "Tech", "Fitness", "Lifestyle", "Business", "Entertainment",
        "Education", "Food", "Travel", "Fashion", "Gaming"
    ]

    return (
        <div className="max-w-4xl mx-auto p-6 space-y-8">
            {/* Header */}
            <div className="text-center">
                <div className="flex justify-center mb-4">
                    <div className="p-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full">
                        <Lightbulb className="h-8 w-8 text-white" />
                    </div>
                </div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                    AI Content Idea Generator
                </h1>
                <p className="text-gray-600 mt-2">
                    Generate viral content ideas tailored to your niche and audience
                </p>
            </div>

            {/* Form */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Sparkles className="h-5 w-5" />
                        Generate Ideas
                    </CardTitle>
                    <CardDescription>
                        Fill in the details below to get personalized content ideas
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <Label htmlFor="topic">Topic/Keyword *</Label>
                                <Input
                                    id="topic"
                                    placeholder="e.g., AI productivity tools"
                                    value={formData.topic}
                                    onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                                    required
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="niche">Niche</Label>
                                <Select value={formData.niche} onValueChange={(value) => setFormData({ ...formData, niche: value })}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select your niche" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {niches.map((niche) => (
                                            <SelectItem key={niche} value={niche.toLowerCase()}>
                                                {niche}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="audience">Target Audience</Label>
                                <Input
                                    id="audience"
                                    placeholder="e.g., Young professionals, ages 25-35"
                                    value={formData.audience}
                                    onChange={(e) => setFormData({ ...formData, audience: e.target.value })}
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="platform">Platform (Optional)</Label>
                                <Select value={formData.platform} onValueChange={(value) => setFormData({ ...formData, platform: value })}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Optimize for platform" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {platforms.map((platform) => (
                                            <SelectItem key={platform.value} value={platform.value}>
                                                {platform.label}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="count">Number of Ideas: {formData.count}</Label>
                            <input
                                type="range"
                                id="count"
                                min="1"
                                max="10"
                                value={formData.count}
                                onChange={(e) => setFormData({ ...formData, count: parseInt(e.target.value) })}
                                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                            />
                            <div className="flex justify-between text-sm text-gray-500">
                                <span>1</span>
                                <span>10</span>
                            </div>
                        </div>

                        <Button
                            type="submit"
                            className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
                            disabled={isLoading || !formData.topic}
                        >
                            {isLoading ? (
                                <>
                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                                    Generating Ideas...
                                </>
                            ) : (
                                <>
                                    <Sparkles className="h-4 w-4 mr-2" />
                                    Generate {formData.count} Ideas
                                </>
                            )}
                        </Button>
                    </form>
                </CardContent>
            </Card>

            {/* Results */}
            {ideas.length > 0 && (
                <div className="space-y-4">
                    <h2 className="text-2xl font-semibold flex items-center gap-2">
                        <TrendingUp className="h-6 w-6" />
                        Generated Ideas
                    </h2>
                    <div className="grid gap-4">
                        {ideas.map((idea, index) => (
                            <Card key={idea.id} className="hover:shadow-lg transition-shadow">
                                <CardContent className="p-6">
                                    <div className="flex justify-between items-start mb-3">
                                        <div className="flex items-center gap-2">
                                            <span className="bg-purple-100 text-purple-600 px-2 py-1 rounded-full text-sm font-medium">
                                                #{index + 1}
                                            </span>
                                            <div className={`w-3 h-3 rounded-full ${getEngagementColor(idea.engagement_score)}`} />
                                            <span className="text-sm text-gray-600">
                                                {idea.engagement_score}% engagement potential
                                            </span>
                                        </div>
                                        {idea.platform_optimized && (
                                            <Badge variant="outline" className="capitalize">
                                                {idea.platform_optimized}
                                            </Badge>
                                        )}
                                    </div>

                                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                                        {idea.title}
                                    </h3>

                                    <p className="text-gray-600 mb-4">
                                        {idea.description}
                                    </p>

                                    {idea.hashtags.length > 0 && (
                                        <div className="flex flex-wrap gap-2">
                                            <Hash className="h-4 w-4 text-gray-400 mt-1" />
                                            {idea.hashtags.map((hashtag, idx) => (
                                                <Badge key={idx} variant="secondary" className="text-xs">
                                                    {hashtag}
                                                </Badge>
                                            ))}
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </div>
            )}
        </div>
    )
}
