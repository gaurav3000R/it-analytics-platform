'use client'

import React from 'react'
import { GlassCard } from './glass-card'
import { Input } from './input'
import { Select } from './select'
import { Textarea } from './textarea'
import { Checkbox } from './checkbox'
import { Radio } from './radio'
import { Label } from './label'
import { ButtonFuturistic } from './button-futuristic'
import { Search, Mail, User, Calendar } from 'lucide-react'

export function FormExamples() {
  return (
    <div className="space-y-8">
      <GlassCard>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Form Examples</h2>
        
        <div className="space-y-6">
          {/* Text Input */}
          <div className="space-y-2">
            <Label required>Full Name</Label>
            <Input type="text" placeholder="Enter your full name" />
          </div>

          {/* Email Input */}
          <div className="space-y-2">
            <Label required>Email Address</Label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input 
                type="email" 
                placeholder="your.email@example.com" 
                className="pl-10"
              />
            </div>
          </div>

          {/* Search Input */}
          <div className="space-y-2">
            <Label>Search</Label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input 
                type="search" 
                placeholder="Search projects..." 
                className="pl-10"
              />
            </div>
          </div>

          {/* Select Dropdown */}
          <div className="space-y-2">
            <Label required>Project Type</Label>
            <Select>
              <option value="">Select a project type</option>
              <option value="web">Web Development</option>
              <option value="mobile">Mobile App</option>
              <option value="desktop">Desktop Application</option>
              <option value="api">API Development</option>
              <option value="data">Data Analytics</option>
            </Select>
          </div>

          {/* Two Column Layout */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Start Date</Label>
              <Input type="date" />
            </div>
            <div className="space-y-2">
              <Label>End Date</Label>
              <Input type="date" />
            </div>
          </div>

          {/* Number Input */}
          <div className="space-y-2">
            <Label>Budget (USD)</Label>
            <Input 
              type="number" 
              placeholder="50000" 
              min="0"
              step="1000"
            />
          </div>

          {/* Textarea */}
          <div className="space-y-2">
            <Label>Project Description</Label>
            <Textarea 
              placeholder="Describe your project in detail..."
              rows={4}
            />
          </div>

          {/* Checkboxes */}
          <div className="space-y-3">
            <Label>Technologies</Label>
            <div className="space-y-2">
              <Checkbox label="React" />
              <Checkbox label="Next.js" />
              <Checkbox label="TypeScript" />
              <Checkbox label="Tailwind CSS" />
            </div>
          </div>

          {/* Radio Buttons */}
          <div className="space-y-3">
            <Label required>Priority Level</Label>
            <div className="space-y-2">
              <Radio name="priority" label="Low" value="low" />
              <Radio name="priority" label="Medium" value="medium" />
              <Radio name="priority" label="High" value="high" />
              <Radio name="priority" label="Critical" value="critical" />
            </div>
          </div>

          {/* Disabled States */}
          <div className="space-y-2">
            <Label>Disabled Input</Label>
            <Input 
              type="text" 
              placeholder="This input is disabled" 
              disabled 
            />
          </div>

          {/* Submit Buttons */}
          <div className="flex gap-3 pt-4">
            <ButtonFuturistic variant="primary" size="md">
              Submit Form
            </ButtonFuturistic>
            <ButtonFuturistic variant="ghost" size="md">
              Cancel
            </ButtonFuturistic>
          </div>
        </div>
      </GlassCard>
    </div>
  )
}
