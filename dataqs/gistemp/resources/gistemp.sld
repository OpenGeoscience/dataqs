<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>gistemp1200_ersstv4</sld:Name>
    <sld:UserStyle>
      <sld:Name>gistemp1200_ersstv4</sld:Name>
      <sld:Title>gistemp1200_ersstv4</sld:Title>
      <sld:FeatureTypeStyle>
        <sld:Name>name</sld:Name>
        <sld:Rule>
          <sld:RasterSymbolizer>
        <Opacity>1.0</Opacity>
        <ChannelSelection>
                <GrayChannel>
                        <SourceChannelName>{latest_band}</SourceChannelName>
                </GrayChannel>
        </ChannelSelection>
        <ColorMap extended="true">
                <ColorMapEntry color="#0000ff" quantity="0" label="0° C"/>
                <ColorMapEntry color="#009933" quantity="250" label = "2.5 °C"/>
                <ColorMapEntry color="#ff9900" quantity="500" label = "5.0 °C"/>
                <ColorMapEntry color="#ff0000" quantity="750" label = "7.5 °C"/>
        </ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>